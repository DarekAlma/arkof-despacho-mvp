"""Enlaza las credenciales creadas en el editor de n8n local con los nodos del flujo.

El JSON versionado (arkof_despacho_workflow.json) trae credenciales de marcador ("CONFIGURAR"), porque los ids
son propios de cada instalación. Este script lee los ids de la base de n8n (solo id, nombre y tipo; nunca los
secretos, que además están cifrados) y genera n8n/.flujo_enlazado.json, que no se versiona.

Uso (con n8n detenido):
    python n8n/enlazar_credenciales.py
    node n8n/iniciar_n8n.mjs importar n8n/.flujo_enlazado.json
    node n8n/iniciar_n8n.mjs activar
"""
import json
import os
import sqlite3
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
carpeta = os.environ.get("N8N_USER_FOLDER") or os.path.join(os.path.expanduser("~"), ".arkof-n8n")
base = os.path.join(carpeta, ".n8n", "database.sqlite")
if not os.path.exists(base):
    sys.exit(f"No se encontró la base de n8n en {base}. Inicie n8n al menos una vez.")

con = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
credenciales = {}
for cid, nombre, tipo in con.execute("select id, name, type from credentials_entity order by updatedAt desc"):
    credenciales.setdefault(tipo, (cid, nombre))  # si hay varias del mismo tipo, la más reciente
con.close()

flujo = json.load(open(os.path.join(RAIZ, "arkof_despacho_workflow.json"), encoding="utf-8"))
faltan = set()
for nodo in flujo["nodes"]:
    for tipo in list(nodo.get("credentials", {})):
        if tipo in credenciales:
            cid, nombre = credenciales[tipo]
            nodo["credentials"][tipo] = {"id": cid, "name": nombre}
            print(f"  {nodo['name']:42} -> {nombre}")
        else:
            faltan.add(tipo)

json.dump(flujo, open(os.path.join(RAIZ, ".flujo_enlazado.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
if faltan:
    print("Sin credencial creada en n8n para:", ", ".join(sorted(faltan)), "(esos nodos fallarán sin detener el flujo)")
print("Listo: n8n/.flujo_enlazado.json")
