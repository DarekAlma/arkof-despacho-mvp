"""Pruebas funcionales del MVP (pytest). Cada prueba valida una regla de negocio del cap. 6.6."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import db, Brigadista  # noqa: E402

DERRAME_MENOR = {"empresa_id": 1, "tipo": "DERRAME_HIDROCARBURO", "municipio": "Acacías",
                 "lat": 3.99, "lon": -73.75, "volumen_bbl": 2}
DERRAME_MAYOR = {"empresa_id": 1, "tipo": "DERRAME_HIDROCARBURO", "municipio": "Puerto Gaitán",
                 "lat": 4.30, "lon": -72.10, "volumen_bbl": 80, "cuerpo_agua": True}
HAZMAT = {"empresa_id": 3, "tipo": "SUSTANCIA_NOCIVA", "municipio": "Villavicencio",
          "lat": 4.15, "lon": -73.63, "volumen_bbl": 1}


def crear(c, datos):
    r = c.post("/api/incidentes", json=datos)
    assert r.status_code == 201, r.json
    return r.json


def test_rn01_clasificacion_por_severidad(cliente):
    assert crear(cliente, DERRAME_MENOR)["nivel"] == 1
    assert crear(cliente, DERRAME_MAYOR)["nivel"] == 3
    assert crear(cliente, HAZMAT)["nivel"] == 2  # sustancia peligrosa => mínimo nivel 2


def test_rn02_rn03_brigada_con_tamano_y_certificacion(cliente):
    inc = crear(cliente, HAZMAT)
    assert len(inc["asignaciones"]) == 5  # 4 requeridos + 1 sobre-convocatoria (RN-07b)
    for a in inc["asignaciones"]:
        b = db.session.get(Brigadista, a["brigadista_id"])
        assert "HAZMAT" in b.certs()
    assert sum(a["rol_en_brigada"] == "lider" for a in inc["asignaciones"]) == 1


def test_rn04_prioriza_cercania(cliente):
    inc = crear(cliente, DERRAME_MENOR)  # en Acacías
    lider = [a for a in inc["asignaciones"] if a["rol_en_brigada"] == "lider"][0]
    assert lider["brigadista"] == "Paola Díaz"  # líder con base en Acacías


def test_rn03_sin_doble_asignacion(cliente):
    a = crear(cliente, DERRAME_MENOR)
    b = crear(cliente, DERRAME_MENOR)
    ids_a = {x["brigadista_id"] for x in a["asignaciones"]}
    ids_b = {x["brigadista_id"] for x in b["asignaciones"]}
    assert not ids_a & ids_b


def test_rn05_reserva_de_kit(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    tipos = [e["tipo"] for e in inc["equipos"]]
    assert tipos.count("KIT_ANTIDERRAME") == 1 and tipos.count("VEHICULO") == 1
    assert all(e["estado"] == "reservado" for e in inc["equipos"])


def test_rn07_confirmacion_completa_brigada(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    for a in inc["asignaciones"]:
        cliente.post(f"/confirmar/{a['token']}", data={"respuesta": "si"})
    d = cliente.get(f"/api/incidentes/{inc['id']}").json
    assert d["estado"] == "confirmado" and d["confirmado_en"]


def test_rn08_escalamiento_por_rechazo(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    rechaza = inc["asignaciones"][0]
    cliente.get(f"/confirmar/{rechaza['token']}?respuesta=no")
    d = cliente.get(f"/api/incidentes/{inc['id']}").json
    assert len(d["asignaciones"]) == 3
    assert any(e["tipo"] == "ESCALAMIENTO" for e in d["eventos"])


def test_rn08_escalamiento_por_sla_vencido(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    r = cliente.post(f"/api/incidentes/{inc['id']}/verificar-sla", json={"forzar": True}).json
    assert r["accion"] == "reasignado"
    d = cliente.get(f"/api/incidentes/{inc['id']}").json
    assert sum(a["estado"] == "vencido" for a in d["asignaciones"]) == 2


def test_rn09_recursos_insuficientes(cliente):
    for _ in range(3):
        crear(cliente, DERRAME_MAYOR)
    d = crear(cliente, DERRAME_MAYOR)
    assert d["recursos_insuficientes"] is True


def test_rn10_rn11_cierre_libera_recursos_y_trazabilidad(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    for a in inc["asignaciones"]:
        cliente.post(f"/confirmar/{a['token']}", data={"respuesta": "si"})
    for estado in ("en_ruta", "en_sitio", "controlado"):
        assert cliente.post(f"/api/incidentes/{inc['id']}/estado", json={"estado": estado}).status_code == 200
    d = cliente.post(f"/api/incidentes/{inc['id']}/estado", json={"estado": "cerrado", "notas": "Contenido"}).json
    assert d["estado"] == "cerrado"
    assert all(e["estado"] == "disponible" for e in d["equipos"])
    assert cliente.get("/api/kpis").json["trazabilidad_completa_pct"] == 100.0


def test_transicion_invalida(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    r = cliente.post(f"/api/incidentes/{inc['id']}/estado", json={"estado": "en_sitio"})
    assert r.status_code == 409


def test_brigadista_liberado_tras_cierre_puede_reasignarse(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    for a in inc["asignaciones"]:
        cliente.post(f"/confirmar/{a['token']}", data={"respuesta": "si"})
    cliente.post(f"/api/incidentes/{inc['id']}/estado", json={"estado": "cerrado", "notas": "ok"})
    nuevo = crear(cliente, DERRAME_MENOR)
    assert {a["brigadista_id"] for a in inc["asignaciones"]} & {a["brigadista_id"] for a in nuevo["asignaciones"]}


def test_rn07b_sobreconvocatoria_libera_excedentes(cliente):
    inc = crear(cliente, HAZMAT)  # nivel 2: 4 requeridos + 1 extra
    for a in inc["asignaciones"][:4]:
        cliente.post(f"/confirmar/{a['token']}", data={"respuesta": "si"})
    d = cliente.get(f"/api/incidentes/{inc['id']}").json
    assert d["estado"] == "confirmado"
    assert sum(a["estado"] == "no_requerido" for a in d["asignaciones"]) == 1


def test_rn05_equipos_de_la_base_mas_cercana(cliente):
    inc = crear(cliente, DERRAME_MENOR)  # Acacías
    assert {e["base"] for e in inc["equipos"]} == {"Acacías"}


def test_ver_como_brigadista_abre_pagina_sin_responder(cliente):
    """Botón "Ver como brigadista" del detalle: abre /confirmar/<token> sin registrar respuesta."""
    inc = crear(cliente, DERRAME_MENOR)
    for a in inc["asignaciones"]:
        r = cliente.get(f"/confirmar/{a['token']}")
        assert r.status_code == 200
        html = r.get_data(as_text=True)
        assert a["brigadista"] in html and inc["codigo"] in html
        assert 'value="si"' in html  # sigue pendiente: muestra los botones de respuesta
    d = cliente.get(f"/api/incidentes/{inc['id']}").json
    assert all(a["estado"] == "pendiente" for a in d["asignaciones"])
    assert d["estado"] == "notificado"
    assert cliente.get("/confirmar/token-inexistente").status_code == 404
    # El detalle enlaza cada fila de la brigada con su página de confirmación en otra pestaña
    fuente = open(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src", "Consola.jsx"),
                  encoding="utf-8").read()
    assert 'href={`/confirmar/${a.token}`} target="_blank"' in fuente
    assert "Ver como brigadista" in fuente


# ---------------------------------------------------------------- RN-04: control de fatiga (prioriza, no excluye)
def dar_atenciones(nombre, cantidad, hace_horas=1):
    """Registra atenciones cerradas de un brigadista hace `hace_horas` horas."""
    from datetime import timedelta
    from models import Asignacion, Incidente, ahora
    b = Brigadista.query.filter_by(nombre=nombre).one()
    for _ in range(cantidad):
        cierre = ahora() - timedelta(hours=hace_horas)
        inc = Incidente(tipo="DERRAME_HIDROCARBURO", municipio="Acacías", lat=3.99, lon=-73.75, nivel=1,
                        estado="cerrado", reportado_en=cierre, cerrado_en=cierre)
        db.session.add(Asignacion(incidente=inc, brigadista=b, rol_en_brigada=b.rol, estado="confirmado"))
    db.session.commit()
    return b


def test_rn04_fatiga_va_al_final_si_hay_alternativa(cliente):
    dar_atenciones("Paola Díaz", 2)  # líder más cercana a Acacías, pero cansada
    inc = crear(cliente, DERRAME_MENOR)
    lider = [a for a in inc["asignaciones"] if a["rol_en_brigada"] == "lider"][0]
    assert lider["brigadista"] != "Paola Díaz"  # se prefiere a otro líder descansado
    assert not inc["convocado_con_fatiga"]
    assert not any(e["tipo"] == "CONVOCATORIA_CON_FATIGA" for e in inc["eventos"])


def test_rn04_fatiga_no_excluye_si_no_hay_alternativa(cliente):
    for lider in ("Paola Díaz", "Andrés Rojas", "Jhon Castro", "Luisa Mejía"):
        dar_atenciones(lider, 2)  # todos los líderes están cansados
    inc = crear(cliente, DERRAME_MENOR)
    lider = [a for a in inc["asignaciones"] if a["rol_en_brigada"] == "lider"][0]
    assert lider["brigadista"] == "Paola Díaz"  # se convoca igual, a la más cercana
    assert not inc["recursos_insuficientes"]  # la brigada no queda incompleta
    assert inc["convocado_con_fatiga"]
    evento = next(e for e in inc["eventos"] if e["tipo"] == "CONVOCATORIA_CON_FATIGA")
    assert "Paola Díaz" in evento["detalle"] and "RN-04" in evento["detalle"]
    import notificador
    assert any(m["evento"] == "alerta_coordinador" and "fatiga" in m["motivo"] for m in notificador.BANDEJA)
    # La bandeja guarda el más reciente primero: el despacho a la brigada debe salir antes que la alerta
    eventos = [m["evento"] for m in notificador.BANDEJA if m.get("incidente", {}).get("codigo") == inc["codigo"]]
    assert eventos.index("alerta_coordinador") < eventos.index("despacho")


def test_rn04_la_ventana_es_de_24_horas(cliente):
    paola = dar_atenciones("Paola Díaz", 3, hace_horas=30)  # atenciones de hace más de 24 h
    assert paola.atenciones_recientes() == 0
    inc = crear(cliente, DERRAME_MENOR)
    assert [a for a in inc["asignaciones"] if a["rol_en_brigada"] == "lider"][0]["brigadista"] == "Paola Díaz"


def test_rn10_cierre_cuenta_para_la_fatiga(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    for a in inc["asignaciones"]:
        cliente.post(f"/confirmar/{a['token']}", data={"respuesta": "si"})
    cliente.post(f"/api/incidentes/{inc['id']}/estado", json={"estado": "cerrado", "notas": "ok"})
    paola = next(b for b in cliente.get("/api/brigadistas").json if b["nombre"] == "Paola Díaz")
    assert paola["atenciones_24h"] == 1
