"""Carga tres incidentes de demostración contra una instancia en ejecución del MVP.

Uso (con la app corriendo):  python demo_escenarios.py [http://localhost:5000]
Ingresa como coordinador con CLAVE_DEMO (por defecto la de semilla.py).
1) Nivel 1 en Acacías: confirmado, atendido y cerrado (trazabilidad completa).
2) Nivel 2 con sustancia nociva en Villavicencio: un rechazo cubierto por sobre-convocatoria.
3) Nivel 3 con cuerpo de agua en Puerto Gaitán: brigada de 6 + 2 notificada, pendiente.
"""
import os
import sys
import time

import requests
from dotenv import load_dotenv

from semilla import CLAVE_DEMO_POR_DEFECTO

load_dotenv()
B = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000").rstrip("/")
S = requests.Session()  # guarda la cookie de sesión del coordinador
S.post(B + "/api/auth/ingresar", json={"usuario": "coordinador",
                                       "clave": os.getenv("CLAVE_DEMO") or CLAVE_DEMO_POR_DEFECTO},
       timeout=15).raise_for_status()


def post(ruta, datos):
    r = S.post(B + ruta, json=datos, timeout=15)
    r.raise_for_status()
    return r.json()


def responder(token, si=True):
    requests.post(f"{B}/confirmar/{token}", data={"respuesta": "si" if si else "no"}, timeout=15)


S.post(B + "/api/demo/reiniciar", timeout=15).raise_for_status()
a = post("/api/incidentes", {"empresa_id": 2, "tipo": "DERRAME_HIDROCARBURO", "municipio": "Acacías",
                             "lat": 3.99, "lon": -73.76, "volumen_bbl": 3,
                             "descripcion": "Fuga en línea de transferencia de ACPM"})
time.sleep(1.5)
for x in a["asignaciones"]:
    responder(x["token"]); time.sleep(0.8)
for estado in ("en_ruta", "en_sitio", "controlado"):
    post(f"/api/incidentes/{a['id']}/estado", {"estado": estado}); time.sleep(0.6)
post(f"/api/incidentes/{a['id']}/estado", {"estado": "cerrado",
     "notas": "Derrame contenido con barrera y absorbente; residuos entregados a gestor autorizado."})

b = post("/api/incidentes", {"empresa_id": 3, "tipo": "SUSTANCIA_NOCIVA", "municipio": "Villavicencio",
                             "lat": 4.153, "lon": -73.635, "volumen_bbl": 1,
                             "descripcion": "Derrame de ácido en bodega de almacenamiento"})
time.sleep(1)
responder(b["asignaciones"][0]["token"]); time.sleep(0.8)
responder(b["asignaciones"][1]["token"], si=False); time.sleep(0.8)
responder(b["asignaciones"][2]["token"])

post("/api/incidentes", {"empresa_id": 1, "tipo": "DERRAME_HIDROCARBURO", "municipio": "Puerto Gaitán",
                         "lat": 4.314, "lon": -72.082, "volumen_bbl": 70, "cuerpo_agua": True,
                         "descripcion": "Ruptura de tubería de flujo cerca de un caño"})
print("Escenarios cargados. KPIs:", S.get(B + "/api/kpis", timeout=15).json())
