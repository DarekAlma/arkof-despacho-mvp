"""Integración con n8n (capa de automatización de notificaciones).

La aplicación NO envía correos ni SMS directamente: publica un evento JSON en el
webhook de n8n, y el flujo de n8n se encarga de enviar correo (SMTP) y SMS
(Twilio), de esperar el SLA (nodo Wait) y de invocar de vuelta la API para
verificar confirmaciones. Así la lógica de negocio (Flask) queda desacoplada de
los canales de mensajería, y agregar WhatsApp (p. ej. Evolution API) en el
futuro solo exige modificar el flujo de n8n.

Si N8N_WEBHOOK_URL no está configurada, el MVP funciona en "modo simulación"
para que la demostración no dependa de credenciales externas. En ambos modos
cada evento queda en una bandeja de salida local (visible en la UI) con el canal
por el que salió, de modo que los enlaces de confirmación siempre son visibles.
"""
import os
from datetime import datetime, timezone

import requests

import reglas as R

BANDEJA = []  # últimos eventos publicados (vía n8n o simulados)
BANDEJA_SIMULADA = BANDEJA  # nombre anterior, se conserva por compatibilidad


def base_url():
    return os.getenv("PUBLIC_BASE_URL", "http://localhost:5000").rstrip("/")


def payload(inc, asignaciones, **extra):
    return {
        "incidente": {"id": inc.id, "codigo": inc.codigo, "tipo": inc.tipo, "nivel": inc.nivel,
                      "municipio": inc.municipio, "lat": inc.lat, "lon": inc.lon,
                      "empresa": inc.empresa.nombre if inc.empresa else None,
                      "empresa_email": inc.empresa.contacto_email if inc.empresa else None,
                      "descripcion": inc.descripcion},
        "sla_minutos": R.SLA_CONFIRMACION_MIN.get(inc.nivel or 1, 5),
        "url_verificar_sla": f"{base_url()}/api/incidentes/{inc.id}/verificar-sla",
        "coordinador_email": os.getenv("COORDINADOR_EMAIL", "coordinador@arkof.example"),
        "coordinador_telefono": os.getenv("COORDINADOR_TELEFONO", "+570000000000"),
        # Canal de DEMOSTRACIÓN: con DEMO_TELEGRAM_CHAT_ID, n8n envía además un mensaje de Telegram. El SMS (Twilio)
        # sigue siendo el canal de producción; Telegram requiere datos móviles y no lo reemplaza en campo.
        "coordinador_telegram": os.getenv("DEMO_TELEGRAM_CHAT_ID", ""),
        "destinatarios": [{
            "nombre": a.brigadista.nombre, "rol": a.rol_en_brigada,
            "email": a.brigadista.email, "telefono": a.brigadista.telefono,
            "distancia_km": round(a.distancia_km or 0, 1),
            "url_confirmar": f"{base_url()}/confirmar/{a.token}",
            "url_rechazar": f"{base_url()}/confirmar/{a.token}?respuesta=no",
            "url_portal": f"{base_url()}/",
            "usuario": a.brigadista.usuario.usuario if a.brigadista.usuario else None,
            "telegram_chat_id": os.getenv("DEMO_TELEGRAM_CHAT_ID", ""),
        } for a in asignaciones],
        **extra,
    }


def enviar(evento, datos):
    cuerpo = {"evento": evento, "emitido_en": datetime.now(timezone.utc).isoformat(), **datos}
    url = os.getenv("N8N_WEBHOOK_URL", "").strip()
    if url:
        try:
            r = requests.post(url, json=cuerpo, timeout=8,
                              headers={"X-ARKOF-Token": os.getenv("N8N_SHARED_SECRET", "")})
            r.raise_for_status()
            _registrar(cuerpo, "n8n")
            return "n8n"
        except requests.RequestException as exc:  # degradación controlada
            _registrar(cuerpo, "simulación (n8n no respondió)", error=str(exc))
            return "simulación (n8n no respondió)"
    _registrar(cuerpo, "simulación")
    return "simulación"


def _registrar(cuerpo, canal, error=None):
    BANDEJA.insert(0, {**cuerpo, "canal": canal, "error_n8n": error})
    del BANDEJA[50:]
    if canal != "n8n":
        dest = ", ".join(d["nombre"] for d in cuerpo.get("destinatarios", [])) or "coordinador/cliente"
        print(f"[NOTIFICACIÓN SIMULADA] {cuerpo['evento']} -> {dest}")
