"""Pruebas de autenticación por rol, portal del brigadista y bandeja de notificaciones."""

import notificador
from conftest import ingresar
from test_despacho import DERRAME_MENOR, crear


def test_api_exige_sesion(app):
    anonimo = app.test_client()
    assert anonimo.get("/api/incidentes").status_code == 401
    assert anonimo.post("/api/incidentes", json=DERRAME_MENOR).status_code == 401
    assert anonimo.get("/api/salud").status_code == 200  # pública
    assert anonimo.get("/api/auth/yo").status_code == 401


def test_ingreso_con_clave_incorrecta(app):
    c = app.test_client()
    r = c.post("/api/auth/ingresar", json={"usuario": "coordinador", "clave": "otra"})
    assert r.status_code == 401
    assert c.get("/api/incidentes").status_code == 401


def test_cada_brigadista_tiene_cuenta(cliente):
    brigadistas = cliente.get("/api/brigadistas").json
    assert len(brigadistas) == 14 and all(b["usuario"] for b in brigadistas)
    assert "paola.diaz" in {b["usuario"] for b in brigadistas}  # sin tildes, nombre.apellido


def test_salir_cierra_la_sesion(cliente):
    assert cliente.post("/api/auth/salir").status_code == 200
    assert cliente.get("/api/incidentes").status_code == 401


def test_brigadista_no_accede_a_la_consola(app):
    b = ingresar(app, "paola.diaz")
    assert b.get("/api/auth/yo").json["rol"] == "brigadista"
    assert b.get("/api/incidentes").status_code == 403
    assert b.post("/api/incidentes", json=DERRAME_MENOR).status_code == 403
    assert b.get("/api/kpis").status_code == 403


def test_coordinador_no_usa_el_portal_del_brigadista(cliente):
    assert cliente.get("/api/mi/asignaciones").status_code == 403


def test_brigadista_ve_y_confirma_solo_lo_suyo(app, cliente):
    inc = crear(cliente, DERRAME_MENOR)  # Acacías: la líder es Paola Díaz
    paola = ingresar(app, "paola.diaz")
    mias = paola.get("/api/mi/asignaciones").json["asignaciones"]
    assert len(mias) == 1 and mias[0]["incidente"]["codigo"] == inc["codigo"]
    assert "token" not in mias[0]  # el portal no expone el enlace de un solo uso
    assert mias[0]["estado"] == "pendiente" and mias[0]["vence_en"]

    ajena = next(a for a in inc["asignaciones"] if a["brigadista"] != "Paola Díaz")
    assert paola.post(f"/api/mi/asignaciones/{ajena['id']}/responder", json={"acepta": True}).status_code == 404

    r = paola.post(f"/api/mi/asignaciones/{mias[0]['id']}/responder", json={"acepta": True})
    assert r.status_code == 200 and r.json["estado"] == "confirmado"
    assert any(x["yo"] for x in r.json["brigada"]) and r.json["equipos"]  # ve su brigada y el kit
    # Responder dos veces no cambia la decisión
    assert paola.post(f"/api/mi/asignaciones/{mias[0]['id']}/responder", json={"acepta": False}).status_code == 409

    d = cliente.get(f"/api/incidentes/{inc['id']}").json
    assert any("portal del brigadista" in e["detalle"] for e in d["eventos"])  # RN-11: queda el canal


def test_rechazo_desde_el_portal_dispara_reemplazo(app, cliente):
    inc = crear(cliente, DERRAME_MENOR)
    paola = ingresar(app, "paola.diaz")
    aid = paola.get("/api/mi/asignaciones").json["asignaciones"][0]["id"]
    assert paola.post(f"/api/mi/asignaciones/{aid}/responder", json={"acepta": False}).json["estado"] == "rechazado"
    d = cliente.get(f"/api/incidentes/{inc['id']}").json
    assert any(e["tipo"] == "ESCALAMIENTO" for e in d["eventos"])  # RN-08


def test_enlace_del_sms_funciona_sin_sesion(app, cliente):
    """Decisión de diseño (doc. 6.4): el enlace de un solo uso no exige iniciar sesión."""
    inc = crear(cliente, DERRAME_MENOR)
    anonimo = app.test_client()
    a = inc["asignaciones"][0]
    r = anonimo.post(f"/confirmar/{a['token']}", data={"respuesta": "si"}, follow_redirects=True)
    assert r.status_code == 200 and "Respuesta registrada" in r.get_data(as_text=True)
    assert "Confirmado" in r.get_data(as_text=True)
    assert cliente.get(f"/api/incidentes/{inc['id']}").json["asignaciones"][0]["estado"] == "confirmado"


def test_verificar_sla_con_secreto_o_sesion_de_coordinador(app, cliente, monkeypatch):
    inc = crear(cliente, DERRAME_MENOR)
    monkeypatch.setenv("N8N_SHARED_SECRET", "secreto-de-prueba")
    ruta = f"/api/incidentes/{inc['id']}/verificar-sla"
    assert app.test_client().post(ruta, json={}).status_code == 401  # sin secreto ni sesión
    assert app.test_client().post(ruta, json={}, headers={"X-ARKOF-Token": "secreto-de-prueba"}).status_code == 200
    assert cliente.post(ruta, json={"forzar": True}).json["accion"] == "reasignado"  # botón de la consola


def test_bandeja_registra_eventos_con_enlaces(cliente):
    notificador.BANDEJA.clear()
    crear(cliente, DERRAME_MENOR)
    evento = cliente.get("/api/notificaciones").json[0]
    assert evento["evento"] == "despacho" and evento["canal"] == "simulación"
    d = evento["destinatarios"][0]
    assert "/confirmar/" in d["url_confirmar"] and d["usuario"] and d["url_portal"]


def test_payload_lleva_telegram_de_demostracion(cliente, monkeypatch):
    """Canal de demostración: con DEMO_TELEGRAM_CHAT_ID el evento lleva el chat de Telegram; sin ella va vacío."""
    notificador.BANDEJA.clear()
    crear(cliente, DERRAME_MENOR)
    assert notificador.BANDEJA[0]["destinatarios"][0]["telegram_chat_id"] == ""
    monkeypatch.setenv("DEMO_TELEGRAM_CHAT_ID", "123456789")
    crear(cliente, DERRAME_MENOR)
    evento = notificador.BANDEJA[0]
    assert evento["destinatarios"][0]["telegram_chat_id"] == "123456789"
    assert evento["coordinador_telegram"] == "123456789"


def test_plazo_expuesto_coincide_con_reglas(cliente):
    inc = crear(cliente, DERRAME_MENOR)
    assert inc["sla_minutos"] == 5  # RN-07, nivel 1
    assert all(a["vence_en"] for a in inc["asignaciones"])


def test_previsualizar_aplica_reglas_sin_registrar(cliente):
    datos = dict(DERRAME_MENOR, volumen_bbl=60)  # RN-01: >= 50 bbl => nivel 3
    p = cliente.post("/api/incidentes/previsualizar", json=datos).json
    assert (p["nivel"], p["brigada"], p["lideres"], p["sobreconvocatoria"]) == (3, 6, 2, 2)
    assert p["kit"]["VEHICULO"] == 2 and p["certificacion"] == "ANTIDERRAME"  # RN-06 y RN-03
    assert cliente.get("/api/incidentes").json == []  # no registró nada
    assert crear(cliente, datos)["nivel"] == p["nivel"]  # coincide con el despacho real


def test_resumen_de_simulacion(cliente):
    s = cliente.get("/api/simulacion").json
    assert s["disponible"] and s["asis_media"] > s["tobe_media"] and set(s["por_nivel"]) == {"1", "2", "3"}


def test_enlace_explica_estados_finales(app, cliente):
    """Pendiente 3: la página del enlace muestra un mensaje claro cuando la asignación ya no admite respuesta."""
    inc = crear(cliente, DERRAME_MENOR)
    token = inc["asignaciones"][0]["token"]
    cliente.post(f"/api/incidentes/{inc['id']}/verificar-sla", json={"forzar": True})  # todo pasa a vencido
    anonimo = app.test_client()
    html = anonimo.get(f"/confirmar/{token}").get_data(as_text=True)
    assert "Plazo vencido" in html and "cupo se reasignó" in html and 'value="si"' not in html
    r = anonimo.post(f"/confirmar/{token}", data={"respuesta": "si"})
    assert r.status_code == 303 and "resultado=ya" in r.headers["Location"]  # recargar no reenvía
    assert "ya no admitía respuesta" in anonimo.get(r.headers["Location"]).get_data(as_text=True)
