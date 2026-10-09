"""Simulación de eventos discretos: AS-IS (manual) vs TO-BE (motor real del MVP).

- TO-BE: ejecuta el motor_despacho REAL (mismas reglas que la aplicación) con un
  reloj simulado; solo se modela el comportamiento humano de los brigadistas.
- AS-IS: modelo de llamadas secuenciales calibrado con las estimaciones del cap. 2.

Todos los parámetros de comportamiento humano son SUPUESTOS del equipo (ver
PARAMS) y deben recalibrarse con datos reales de ARKOF en un piloto.

Uso:  python simular_escenarios.py [n_incidentes] [semilla]
Salida: resultados_simulacion.json
"""
import json
import os
import random
import sys
import tempfile
from datetime import datetime, timedelta
from statistics import mean, median

os.environ.pop("N8N_WEBHOOK_URL", None)
sys.path.insert(0, os.path.dirname(__file__))

import motor_despacho as M  # noqa: E402
import models  # noqa: E402
import notificador  # noqa: E402
from app import crear_app  # noqa: E402
from models import db, Brigadista, Asignacion  # noqa: E402

PARAMS = {
    "mezcla_niveles": {1: 0.50, 2: 0.35, 3: 0.15},
    # TO-BE (comportamiento humano ante la notificación)
    "latencia_entrega_min": 0.5,
    "p_confirma": 0.80, "p_rechaza": 0.10,  # resto: no responde dentro del SLA
    "mediana_respuesta_min": 2.5,
    # AS-IS (proceso manual)
    "registro_inicial_min": (3, 5),
    "duracion_llamada_min": (2, 3),
    "p_contacto_efectivo": 0.65,
    "verificacion_equipos_min": (5, 8),
    "registro_manual_min": (3, 5),
    "coordinacion_por_brigadista_min": (0.8, 1.2),
    "p_error_asignacion_asis": 0.20,  # brigada/equipo no disponible real (cap. 2)
    "reproceso_min": (6, 10),
}


class Reloj:
    def __init__(self):
        self.t = datetime(2026, 10, 1, 8, 0, 0)

    def __call__(self):
        return self.t


def escenario(nivel, rnd):
    base = {1: ("Acacías", 3.99, -73.75, 2, False, False),
            2: ("Villavicencio", 4.16, -73.60, 20, True, False),
            3: ("Puerto Gaitán", 4.30, -72.10, 80, True, True)}[nivel]
    tipo = "DERRAME_HIDROCARBURO" if nivel != 2 or rnd.random() < 0.6 else "SUSTANCIA_NOCIVA"
    if tipo == "SUSTANCIA_NOCIVA":
        base = ("Villavicencio", 4.16, -73.60, 1, False, False)
    m, lat, lon, vol, agua, com = base
    return {"empresa_id": rnd.randint(1, 3), "tipo": tipo, "municipio": m, "lat": lat, "lon": lon,
            "volumen_bbl": vol, "cuerpo_agua": agua, "comunidad_cercana": com, "canal": "portal"}


def simular_tobe(n, rnd, reloj):
    resultados = []
    for i in range(n):
        for b in Brigadista.query.all():
            b.estado = "disponible"
        db.session.commit()
        nivel = rnd.choices(list(PARAMS["mezcla_niveles"]), weights=PARAMS["mezcla_niveles"].values())[0]
        # Supuesto del modelo: cada incidente encuentra al personal descansado. Los incidentes se separan más
        # que la ventana de fatiga (RN-04), así las atenciones anteriores ya no cuentan.
        reloj.t += timedelta(hours=M.R.VENTANA_FATIGA_HORAS + 1)
        inc = M.registrar_y_despachar(escenario(nivel, rnd))
        t0 = inc.reportado_en
        respuestas = {}  # asignacion_id -> (momento, acepta) o None si no responde

        def programar():
            for a in inc.asignaciones:
                if a.estado == "pendiente" and a.id not in respuestas:
                    u = rnd.random()
                    demora = PARAMS["latencia_entrega_min"] + rnd.lognormvariate(0, 0.5) * PARAMS["mediana_respuesta_min"]
                    if u < PARAMS["p_confirma"]:
                        respuestas[a.id] = (a.notificado_en + timedelta(minutes=demora), True)
                    elif u < PARAMS["p_confirma"] + PARAMS["p_rechaza"]:
                        respuestas[a.id] = (a.notificado_en + timedelta(minutes=demora), False)
                    else:
                        respuestas[a.id] = None

        programar()
        guardia = 0
        while inc.estado == "notificado" and guardia < 60:
            guardia += 1
            pendientes = [a for a in inc.asignaciones if a.estado == "pendiente"]
            if not pendientes:
                break
            proximas = [(respuestas[a.id][0], a) for a in pendientes if respuestas.get(a.id)]
            sla = min(a.notificado_en for a in pendientes) + timedelta(minutes=M.R.SLA_CONFIRMACION_MIN[inc.nivel])
            if proximas and min(p[0] for p in proximas) <= sla:
                momento, a = min(proximas, key=lambda p: p[0])
                reloj.t = momento
                M.registrar_respuesta(a.token, respuestas[a.id][1])
            else:
                reloj.t = sla
                r = M.verificar_sla(inc)
                if r["accion"] == "escalado_a_coordinador":
                    break
            programar()
        conf = inc.confirmado_en
        resultados.append({
            "nivel": inc.nivel,
            "min_reporte_a_notificacion": (inc.notificado_en - t0).total_seconds() / 60,
            "min_reporte_a_brigada_confirmada": (conf - t0).total_seconds() / 60 if conf else None,
            "rondas_escalamiento": inc.rondas_escalamiento,
            "reasignaciones": sum(1 for a in inc.asignaciones if a.estado in ("vencido", "rechazado")),
            "asignaciones": len(inc.asignaciones),
            "escalado_a_coordinador": inc.estado == "notificado",
            "recursos_insuficientes": inc.recursos_insuficientes,
        })
        if inc.estado != "cerrado":
            M.cerrar(inc, "Cierre de simulación", "simulador")
    return resultados


def simular_asis(n, rnd):
    P, res = PARAMS, []
    u = lambda r: rnd.uniform(*r)  # noqa: E731
    for _ in range(n):
        nivel = rnd.choices(list(P["mezcla_niveles"]), weights=P["mezcla_niveles"].values())[0]
        requeridos = M.R.TAMANO_BRIGADA[nivel]
        t = u(P["registro_inicial_min"])
        verif = 0.0
        conseguidos = 0
        while conseguidos < requeridos:
            d = u(P["duracion_llamada_min"])
            t += d; verif += d
            if rnd.random() < P["p_contacto_efectivo"]:
                conseguidos += 1
        d = u(P["verificacion_equipos_min"]); t += d; verif += d
        t += u(P["registro_manual_min"])
        t += requeridos * u(P["coordinacion_por_brigadista_min"])
        error = rnd.random() < P["p_error_asignacion_asis"]
        if error:
            t += u(P["reproceso_min"])
        res.append({"nivel": nivel, "min_reporte_a_despacho": t, "min_verificacion": verif, "reproceso": error})
    return res


def resumen(valores):
    v = sorted(x for x in valores if x is not None)
    if not v:
        return None
    p90 = v[min(len(v) - 1, int(0.9 * len(v)))]
    return {"n": len(v), "media": round(mean(v), 2), "mediana": round(median(v), 2),
            "p90": round(p90, 2), "min": round(v[0], 2), "max": round(v[-1], 2)}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    semilla_rnd = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    rnd = random.Random(semilla_rnd)
    reloj = Reloj()
    M.ahora = reloj  # reloj simulado inyectado en el motor
    models.ahora = reloj
    tmp = tempfile.mkdtemp()
    app = crear_app(f"sqlite:///{tmp}/sim.db")
    with app.app_context():
        tobe = simular_tobe(n, rnd, reloj)
    asis = simular_asis(n, random.Random(semilla_rnd))
    notificador.BANDEJA_SIMULADA.clear()

    salida = {"parametros": PARAMS, "n": n, "semilla": semilla_rnd, "por_nivel": {}}
    salida["tobe"] = {
        "reporte_a_notificacion_min": resumen([r["min_reporte_a_notificacion"] for r in tobe]),
        "reporte_a_brigada_confirmada_min": resumen([r["min_reporte_a_brigada_confirmada"] for r in tobe]),
        "tasa_reasignacion_pct": round(100 * sum(r["reasignaciones"] for r in tobe) / sum(r["asignaciones"] for r in tobe), 1),
        "incidentes_con_escalamiento_pct": round(100 * sum(1 for r in tobe if r["rondas_escalamiento"]) / n, 1),
        "escalados_a_coordinador_pct": round(100 * sum(r["escalado_a_coordinador"] for r in tobe) / n, 1),
        "despacho_erroneo_pct": 0.0,
    }
    salida["asis"] = {
        "reporte_a_despacho_min": resumen([r["min_reporte_a_despacho"] for r in asis]),
        "verificacion_min": resumen([r["min_verificacion"] for r in asis]),
        "reproceso_pct": round(100 * sum(r["reproceso"] for r in asis) / n, 1),
    }
    for nv in (1, 2, 3):
        salida["por_nivel"][nv] = {
            "asis_media_min": resumen([r["min_reporte_a_despacho"] for r in asis if r["nivel"] == nv]),
            "tobe_media_min": resumen([r["min_reporte_a_brigada_confirmada"] for r in tobe if r["nivel"] == nv]),
        }
    salida["series"] = {"asis": [round(r["min_reporte_a_despacho"], 2) for r in asis],
                        "tobe": [round(r["min_reporte_a_brigada_confirmada"], 2) for r in tobe
                                 if r["min_reporte_a_brigada_confirmada"] is not None]}
    with open(os.path.join(os.path.dirname(__file__), "resultados_simulacion.json"), "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in salida.items() if k not in ("series", "parametros")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
