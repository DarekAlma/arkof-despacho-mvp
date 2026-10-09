"""Motor de despacho: implementa la lógica de automatización del TO-BE.

Flujo principal (ver capítulo 6.6 del documento):
  registrar -> clasificar (RN-01) -> seleccionar brigada (RN-02/03/04)
  -> reservar equipos (RN-05/06) -> notificar vía n8n -> esperar confirmación (RN-07)
  -> escalar si vence el SLA (RN-08) -> seguimiento de estados -> cierre (RN-10)
Toda acción deja un Evento en la bitácora (RN-11).
"""
import math
import secrets
from datetime import timedelta
from types import SimpleNamespace

import reglas as R
from models import db, ahora, Brigadista, Equipo, Incidente, Asignacion, ReservaEquipo, Evento
import notificador
from semilla import BASES

ROL = {"lider": "líder", "tecnico": "técnico"}
# Textos de la bitácora y del informe (solo presentación; los parámetros de negocio están en reglas.py)
CANAL = {"portal": "el portal del cliente", "telefono": "llamada telefónica", "coordinador": "el coordinador"}
EQUIPO = {"KIT_ANTIDERRAME": "kit antiderrames", "BARRERA": "barrera de contención", "ABSORBENTE": "paca absorbente",
          "KIT_HAZMAT": "kit HAZMAT", "EPP": "juego de EPP", "VEHICULO": "camioneta 4x4"}


class TransicionInvalida(Exception):
    pass


# --------------------------------------------------------------------------- utilidades
def distancia_km(lat1, lon1, lat2, lon2):
    """Distancia haversine en km (aproximación en línea recta)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def plural(n, singular, plural_):
    """Concuerda el número en los textos de la bitácora: 1 técnico, 2 técnicos."""
    return f"{n} {singular if n == 1 else plural_}"


def log(inc, tipo, detalle, actor="sistema"):
    db.session.add(Evento(incidente=inc, tipo=tipo, detalle=detalle, actor=actor, momento=ahora()))


# --------------------------------------------------------------------------- RN-01
def clasificar(inc):
    nivel = 1
    if inc.volumen_bbl >= R.UMBRAL_VOLUMEN_NIVEL2_BBL or inc.tipo in R.TIPOS_PELIGROSOS:
        nivel = 2
    if inc.cuerpo_agua or inc.comunidad_cercana:
        nivel = max(nivel, 2)
    if inc.volumen_bbl >= R.UMBRAL_VOLUMEN_NIVEL3_BBL or (inc.cuerpo_agua and inc.comunidad_cercana) \
            or (inc.tipo in R.TIPOS_PELIGROSOS and inc.comunidad_cercana):
        nivel = 3
    return nivel


# --------------------------------------------------------------------------- RN-02/03/04
def candidatos(inc, excluir_ids=()):
    cert = R.CERT_REQUERIDA.get(inc.tipo)
    ocupados = {a.brigadista_id for a in Asignacion.query.join(Incidente)
                .filter(Asignacion.estado.in_(["pendiente", "confirmado"]), Incidente.estado != "cerrado").all()}
    lista = []
    for b in Brigadista.query.filter_by(estado="disponible").all():
        if b.id in excluir_ids or b.id in ocupados:
            continue                                   # RN-03: evita doble asignación
        if cert and cert not in b.certs():
            continue                                   # RN-03: certificación obligatoria
        carga = b.atenciones_recientes()
        fatigado = carga >= R.MAX_ATENCIONES_24H     # RN-04: no excluye, lo manda al final
        d = distancia_km(b.lat, b.lon, inc.lat, inc.lon)
        lista.append((fatigado, d, carga, b))
    lista.sort(key=lambda t: (t[0], t[1], t[2]))      # RN-04: descansados primero; cercanía; menor carga
    return [(b, d) for _, d, _, b in lista]


def _avisar_fatiga(inc, elegidos):
    """RN-04: si hubo que convocar a alguien con fatiga (no había alternativa), queda en bitácora y se alerta."""
    cansados = [(b, b.atenciones_recientes()) for b, _, _ in elegidos]
    cansados = [(b, n) for b, n in cansados if n >= R.MAX_ATENCIONES_24H]
    if not cansados:
        return
    detalle = ", ".join(f"{b.nombre} ({plural(n, 'atención', 'atenciones')} en {R.VENTANA_FATIGA_HORAS} h)"
                        for b, n in cansados)
    log(inc, "CONVOCATORIA_CON_FATIGA", f"Sin alternativa descansada: se convocó a {detalle}. "
        "El coordinador decide si continúa o activa la ayuda mutua (RN-04).")
    notificador.enviar("alerta_coordinador", notificador.payload(
        inc, [], motivo=f"Brigadista(s) convocado(s) con fatiga: {', '.join(b.nombre for b, _ in cansados)}"))


def seleccionar_brigada(inc, cupos_lider, cupos_tecnico, excluir_ids=()):
    elegidos = []
    for b, d in candidatos(inc, excluir_ids):
        if b.rol == "lider" and cupos_lider > 0:
            elegidos.append((b, d, "lider")); cupos_lider -= 1
        elif cupos_tecnico > 0 and b.rol != "lider":
            elegidos.append((b, d, "tecnico")); cupos_tecnico -= 1
        elif cupos_tecnico > 0 and b.rol == "lider" and cupos_lider == 0:
            elegidos.append((b, d, "tecnico")); cupos_tecnico -= 1
        if cupos_lider == 0 and cupos_tecnico == 0:
            break
    return elegidos, cupos_lider + cupos_tecnico


# --------------------------------------------------------------------------- RN-05/06
def kit_requerido(tipo, nivel):
    kit = dict(R.KIT_EQUIPOS[tipo][nivel])
    kit["VEHICULO"] = math.ceil(R.TAMANO_BRIGADA[nivel] / R.BRIGADISTAS_POR_VEHICULO)
    return kit


def reservar_equipos(inc):
    kit = kit_requerido(inc.tipo, inc.nivel)
    faltantes = {}
    for tipo, cantidad in kit.items():
        libres = Equipo.query.filter_by(tipo=tipo, estado="disponible").all()
        # RN-05: se toman primero los equipos de la base más cercana al incidente
        libres.sort(key=lambda e: distancia_km(*BASES.get(e.base, (inc.lat, inc.lon)), inc.lat, inc.lon))
        disponibles = libres[:cantidad]
        for e in disponibles:
            e.estado = "reservado"
            db.session.add(ReservaEquipo(incidente=inc, equipo=e))
        if len(disponibles) < cantidad:
            faltantes[tipo] = cantidad - len(disponibles)
    return kit, faltantes


def previsualizar(datos):
    """Lo que el sistema haría con este reporte (RN-01/02/03/05/06/07/07b), sin registrar nada."""
    inc = SimpleNamespace(tipo=datos["tipo"], volumen_bbl=float(datos.get("volumen_bbl") or 0),
                          cuerpo_agua=bool(datos.get("cuerpo_agua")),
                          comunidad_cercana=bool(datos.get("comunidad_cercana")))
    nivel = clasificar(inc)
    return {"nivel": nivel, "brigada": R.TAMANO_BRIGADA[nivel], "lideres": R.LIDERES_REQUERIDOS[nivel],
            "sobreconvocatoria": R.SOBRECONVOCATORIA[nivel], "certificacion": R.CERT_REQUERIDA[inc.tipo],
            "sla_minutos": R.SLA_CONFIRMACION_MIN[nivel], "kit": kit_requerido(inc.tipo, nivel)}


# --------------------------------------------------------------------------- proceso principal
def registrar_y_despachar(datos, actor="cliente"):
    inc = Incidente(
        empresa_id=datos.get("empresa_id"), tipo=datos["tipo"], descripcion=datos.get("descripcion", ""),
        municipio=datos.get("municipio"), lat=float(datos["lat"]), lon=float(datos["lon"]),
        volumen_bbl=float(datos.get("volumen_bbl") or 0), cuerpo_agua=bool(datos.get("cuerpo_agua")),
        comunidad_cercana=bool(datos.get("comunidad_cercana")), canal=datos.get("canal", "portal"),
        reportado_en=ahora())
    db.session.add(inc)
    db.session.flush()
    inc.codigo = f"INC-{inc.reportado_en:%Y%m%d}-{inc.id:04d}"
    log(inc, "REPORTE", f"Incidente reportado por {CANAL.get(inc.canal, inc.canal)} en {inc.municipio}.", actor)

    inc.nivel = clasificar(inc)
    log(inc, "CLASIFICACION", f"Nivel {inc.nivel} asignado automáticamente (RN-01).")

    total = R.TAMANO_BRIGADA[inc.nivel]
    lideres = R.LIDERES_REQUERIDOS[inc.nivel]
    extra = R.SOBRECONVOCATORIA[inc.nivel]
    elegidos, faltan = seleccionar_brigada(inc, lideres, total - lideres + extra)
    faltan = max(0, faltan - extra) if len(elegidos) < total else 0
    for b, d, rol in elegidos:
        db.session.add(Asignacion(incidente=inc, brigadista=b, rol_en_brigada=rol, distancia_km=d,
                                  token=secrets.token_urlsafe(16)))
    inc.asignado_en = ahora()
    nombres = ", ".join(f"{b.nombre} ({ROL[rol]}, {d:.0f} km)" for b, d, rol in elegidos)
    log(inc, "ASIGNACION", f"Brigada propuesta: {nombres or 'ninguna'} (RN-02/03/04)"
        + (f"; incluye {plural(extra, 'técnico', 'técnicos')} de sobre-convocatoria (RN-07b)." if extra else "."))

    kit, faltantes = reservar_equipos(inc)
    log(inc, "RESERVA_EQUIPOS", "Kit reservado: " + ", ".join(f"{v} × {EQUIPO.get(k, k)}" for k, v in kit.items()) + " (RN-05/06).")
    if faltan or faltantes:
        inc.recursos_insuficientes = True
        log(inc, "ALERTA_RECURSOS", "Recursos insuficientes: faltan "
                    + "; ".join(filter(None, [plural(faltan, "brigadista", "brigadistas") if faltan else "",
                                              ", ".join(f"{v} × {EQUIPO.get(k, k)}" for k, v in faltantes.items())]))
                    + ". "
                                    "Se requiere decisión del coordinador (p. ej., activar convenio de ayuda mutua) (RN-09).")
    db.session.flush()
    _notificar_asignaciones(inc, [a for a in inc.asignaciones if a.estado == "pendiente"], "despacho")
    _avisar_fatiga(inc, elegidos)  # después del despacho: la brigada se entera primero
    db.session.commit()
    return inc


def _notificar_asignaciones(inc, asignaciones, evento):
    momento = ahora()
    for a in asignaciones:
        a.notificado_en = momento
    inc.notificado_en = inc.notificado_en or momento
    if inc.estado == "reportado":
        inc.estado = "notificado"
    resultado = notificador.enviar(evento, notificador.payload(inc, asignaciones))
    log(inc, "NOTIFICACION", f"{plural(len(asignaciones), 'brigadista notificado', 'brigadistas notificados')} por correo + SMS vía {resultado}.", "n8n")


def registrar_respuesta(token, acepta, canal="enlace del SMS/correo"):
    a = Asignacion.query.filter_by(token=token).first()
    if not a:
        return None, "Token inválido"
    if a.estado != "pendiente":
        return a, f"La asignación ya estaba en estado '{a.estado}'"
    inc = a.incidente
    a.estado = "confirmado" if acepta else "rechazado"
    a.respondido_en = ahora()
    log(inc, "RESPUESTA_BRIGADISTA", f"{a.brigadista.nombre} {'CONFIRMÓ' if acepta else 'RECHAZÓ'} la asignación "
        f"(desde {canal}).",
        f"brigadista:{a.brigadista_id}")
    if acepta:
        a.brigadista.estado = "asignado"
        _evaluar_brigada_completa(inc)
    else:
        _reemplazar(inc, motivo="rechazo")
    db.session.commit()
    return a, "ok"


def _evaluar_brigada_completa(inc):
    requeridos = R.TAMANO_BRIGADA[inc.nivel]
    confirmados = [a for a in inc.asignaciones if a.estado == "confirmado"]
    lideres_ok = sum(a.rol_en_brigada == "lider" for a in confirmados) >= R.LIDERES_REQUERIDOS[inc.nivel]
    if len(confirmados) >= requeridos and lideres_ok and inc.estado == "notificado":
        inc.estado = "confirmado"
        inc.confirmado_en = ahora()
        sobrantes = [a for a in inc.asignaciones if a.estado == "pendiente"]
        for a in sobrantes:
            a.estado = "no_requerido"
        log(inc, "BRIGADA_CONFIRMADA", f"Brigada completa ({len(confirmados)}/{requeridos}). Despacho efectivo."
            + (f" {plural(len(sobrantes), 'convocado en exceso liberado', 'convocados en exceso liberados')} (RN-07b)." if sobrantes else ""))
        notificador.enviar("confirmado", notificador.payload(inc, confirmados))


def deficit(inc):
    """Cupos que no quedarían cubiertos ni por confirmados ni por pendientes."""
    vivos = [a for a in inc.asignaciones if a.estado in ("confirmado", "pendiente")]
    lideres = max(0, R.LIDERES_REQUERIDOS[inc.nivel] - sum(a.rol_en_brigada == "lider" for a in vivos))
    total = max(0, R.TAMANO_BRIGADA[inc.nivel] - len(vivos))
    return lideres, max(0, total - lideres)


def _reemplazar(inc, motivo):
    """RN-08: busca reemplazos solo para el déficit real de la brigada."""
    lideres, tecnicos = deficit(inc)
    if lideres + tecnicos == 0:
        log(inc, "SIN_REEMPLAZO_NECESARIO", f"La sobre-convocatoria cubre la baja por {motivo} (RN-07b).")
        return
    excluir = {a.brigadista_id for a in inc.asignaciones}
    elegidos, faltan = seleccionar_brigada(inc, lideres, tecnicos, excluir)
    nuevas = []
    for b, d, rol in elegidos:
        a = Asignacion(incidente=inc, brigadista=b, rol_en_brigada=rol, distancia_km=d,
                       token=secrets.token_urlsafe(16))
        db.session.add(a)
        nuevas.append(a)
    db.session.flush()
    if nuevas:
        log(inc, "ESCALAMIENTO", f"Reasignación automática por {motivo}: " +
            ", ".join(f"{a.brigadista.nombre} ({ROL[a.rol_en_brigada]})" for a in nuevas) + " (RN-08).")
        _notificar_asignaciones(inc, nuevas, "escalamiento")
        _avisar_fatiga(inc, elegidos)
    if faltan:
        inc.recursos_insuficientes = True
        log(inc, "ALERTA_RECURSOS", f"No hay reemplazo para {plural(faltan, 'cupo', 'cupos')}. Alerta al coordinador (RN-09).")
        notificador.enviar("alerta_coordinador", notificador.payload(inc, [], motivo=f"Faltan {faltan} brigadistas"))


def verificar_sla(inc, forzar=False):
    """RN-07/RN-08: invocado por n8n (nodo Wait) o por el vigilante interno."""
    if inc.estado != "notificado":
        return {"accion": "ninguna", "estado": inc.estado}
    limite = timedelta(minutes=R.SLA_CONFIRMACION_MIN[inc.nivel])
    vencidas = [a for a in inc.asignaciones if a.estado == "pendiente"
                and (forzar or ahora() - a.notificado_en >= limite)]
    if not vencidas:
        return {"accion": "ninguna", "estado": inc.estado}
    for a in vencidas:
        a.estado = "vencido"
    inc.rondas_escalamiento += 1
    log(inc, "SLA_VENCIDO", f"{plural(len(vencidas), 'asignación', 'asignaciones')} sin confirmar en {R.SLA_CONFIRMACION_MIN[inc.nivel]:g} min "
                            f"(ronda {inc.rondas_escalamiento}) (RN-07).")
    if inc.rondas_escalamiento > R.MAX_RONDAS_ESCALAMIENTO:
        log(inc, "ESCALAMIENTO_HUMANO", "Se superó el máximo de rondas automáticas; decisión transferida al coordinador (RN-08).")
        notificador.enviar("alerta_coordinador", notificador.payload(inc, [], motivo="Máximo de rondas de escalamiento"))
        accion = "escalado_a_coordinador"
    else:
        _reemplazar(inc, motivo="vencimiento de SLA")
        accion = "reasignado"
    db.session.commit()
    return {"accion": accion, "estado": inc.estado, "ronda": inc.rondas_escalamiento}


def avanzar_estado(inc, nuevo, actor="coordinador", notas=None):
    if nuevo not in R.TRANSICIONES.get(inc.estado, set()):
        raise TransicionInvalida(f"No se permite pasar de '{inc.estado}' a '{nuevo}'")
    if nuevo == "cerrado":
        return cerrar(inc, notas or "", actor)
    inc.estado = nuevo
    if nuevo == "en_sitio":
        inc.en_sitio_en = ahora()
    log(inc, "CAMBIO_ESTADO", f"Estado actualizado a '{nuevo}'.", actor)
    db.session.commit()
    return inc


def cerrar(inc, notas, actor="coordinador"):
    """RN-10: libera recursos, consolida trazabilidad y dispara el informe al cliente."""
    inc.estado = "cerrado"
    inc.cerrado_en = ahora()
    inc.notas_cierre = notas
    for r in inc.reservas:
        if not r.liberado:
            r.liberado = True
            r.equipo.estado = "disponible"
    for a in inc.asignaciones:
        if a.estado == "confirmado":
            a.brigadista.estado = "disponible"  # la atención cuenta para RN-04 por la fecha de cierre
        elif a.estado == "pendiente":
            a.estado = "vencido"
    log(inc, "CIERRE", f"Incidente cerrado. Recursos liberados. Notas: {notas or '—'}", actor)
    notificador.enviar("cierre", notificador.payload(inc, [], informe=informe(inc)))
    log(inc, "INFORME", "Informe de trazabilidad generado y enviado al cliente (RN-10).", "n8n")
    db.session.commit()
    return inc


def informe(inc):
    return {"codigo": inc.codigo, "empresa": inc.empresa.nombre if inc.empresa else None,
            "tipo": inc.tipo, "nivel": inc.nivel, "municipio": inc.municipio,
            "linea_de_tiempo": [f"{e.momento:%Y-%m-%d %H:%M:%S} UTC | {e.tipo} | {e.detalle}" for e in inc.eventos],
            "brigada": [a.brigadista.nombre for a in inc.asignaciones if a.estado == "confirmado"],
            "equipos": [r.equipo.codigo for r in inc.reservas]}
