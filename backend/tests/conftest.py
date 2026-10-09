"""Aísla las pruebas del archivo backend/.env.

app.py llama a load_dotenv() al importarse, y load_dotenv no pisa variables que ya existen.
Por eso se fijan aquí en vacío ANTES de cualquier import de la app: así las pruebas nunca
publican en el n8n real (ni envían correos o SMS), no exigen el secreto compartido y usan
los plazos normales de RN-07 aunque el .env tenga SLA_DEMO_MIN.
"""
import os
import sys

import pytest

for variable in ("N8N_WEBHOOK_URL", "N8N_SHARED_SECRET", "SLA_DEMO_MIN", "DEMO_EMAIL", "DEMO_TELEFONO",
                 "CLAVE_DEMO", "PUBLIC_BASE_URL", "DEMO_TELEGRAM_CHAT_ID"):
    os.environ[variable] = ""

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import crear_app  # noqa: E402
from models import db  # noqa: E402

CLAVE = "arkof2026"  # clave de demostración de semilla.py (CLAVE_DEMO vacía en conftest.py)


@pytest.fixture()
def app(tmp_path):
    aplicacion = crear_app(f"sqlite:///{tmp_path/'test.db'}")
    with aplicacion.app_context():
        yield aplicacion
        db.session.remove()


@pytest.fixture()
def cliente(app):
    """Cliente con sesión de coordinador (la consola exige autenticación)."""
    c = app.test_client()
    assert c.post("/api/auth/ingresar", json={"usuario": "coordinador", "clave": CLAVE}).status_code == 200
    return c


def ingresar(app, usuario):
    c = app.test_client()
    r = c.post("/api/auth/ingresar", json={"usuario": usuario, "clave": CLAVE})
    assert r.status_code == 200, r.json
    return c


