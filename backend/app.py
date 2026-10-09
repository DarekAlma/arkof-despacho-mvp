"""API REST del MVP de despacho de brigadas — ARKOF S.A.S. (proyecto académico GOTI).

Ejecutar:  python app.py      (ver README para variables de entorno)
"""
import glob
import json
import os
import threading
import time
from statistics import mean

from dotenv import load_dotenv
from flask import Flask, g, jsonify, redirect, request, send_from_directory, abort, render_template, session
from flask_cors import CORS

load_dotenv()

import motor_despacho as M  # noqa: E402
import notificador  # noqa: E402
import semilla  # noqa: E402
from models import db, Incidente, Brigadista, Equipo, EmpresaAfiliada, Asignacion, Usuario  # noqa: E402

DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")


def crear_app(db_uri=None):
    # instance_path fijo: sin él, al correr "python backend/app.py" desde otra carpeta la base SQLite
    # se crearía en <carpeta actual>/instance y la app mostraría datos distintos según dónde se arranque.
    app = Flask(__name__, static_folder=None,
                instance_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance"))
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri or os.getenv("DATABASE_URL", "sqlite:///arkof_despacho.db")
    app.config["JSON_AS_ASCII"] = False
    # La sesión viaja en una cookie firmada; en producción SECRET_KEY debe ser un valor aleatorio propio.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or "arkof-dev-cambiar-en-produccion"
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    CORS(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not Brigadista.query.first():
            semilla.cargar()
        elif not Usuario.query.first():
            semilla.crear_cuentas()  # base anterior a la autenticación: se conservan sus datos
    registrar_rutas(app)
    return app


def _secreto_ok():
    secreto = os.getenv("N8N_SHARED_SECRET", "")
    return not secreto or request.headers.get("X-ARKOF-Token") == secreto


def fuentes_de_la_app():
    """@font-face de Barlow y Source Sans 3 tomadas del build de Vite (frontend/dist/assets).

    La página del enlace del SMS no carga el bundle de React; así usa las mismas fuentes que la consola
    sin depender de un CDN. Si el front no está compilado, la plantilla cae a las fuentes del sistema.
    """
    reglas = []
    for familia, archivo, peso in (("Barlow", "barlow-latin-600-normal", 600), ("Barlow", "barlow-latin-700-normal", 700),
                                   ("Source Sans 3", "source-sans-3-latin-400-normal", 400),
                                   ("Source Sans 3", "source-sans-3-latin-600-normal", 600)):
        hallados = glob.glob(os.path.join(DIST, "assets", f"{archivo}-*.woff2"))
        if hallados:
            reglas.append(f'@font-face{{font-family:"{familia}";font-weight:{peso};font-display:swap;'
                          f'src:url(/assets/{os.path.basename(hallados[0])}) format("woff2")}}')
    return "\n".join(reglas)


def usuario_actual():
    uid = session.get("uid")
    return db.session.get(Usuario, uid) if uid else None


def _perfil(u):
    return u.to_dict() | {"brigadista": u.brigadista.to_dict() if u.brigadista else None}


def asignacion_para_brigadista(a):
    """Lo que ve el brigadista de una asignación propia: el incidente y, si confirmó, su brigada y equipos."""
    inc = a.incidente
    d = a.to_dict()
    d.pop("token", None)
    d["incidente"] = {k: v for k, v in inc.to_dict().items() if k in (
        "id", "codigo", "tipo", "nivel", "estado", "municipio", "empresa", "volumen_bbl", "cuerpo_agua",
        "comunidad_cercana", "reportado_en", "sla_minutos")} | {
        "lat": inc.lat, "lon": inc.lon, "descripcion": inc.descripcion}
    if a.estado == "confirmado":
        d["brigada"] = [{"nombre": x.brigadista.nombre, "rol_en_brigada": x.rol_en_brigada,
                         "telefono": x.brigadista.telefono, "yo": x.id == a.id}
                        for x in inc.asignaciones if x.estado == "confirmado"]
        d["equipos"] = [{"codigo": r.equipo.codigo, "descripcion": r.equipo.descripcion, "base": r.equipo.base}
                        for r in inc.reservas if not r.liberado]
    return d


def registrar_rutas(app):
    @app.before_request
    def control_de_acceso():
        """Toda la API exige sesión: /api/mi/* es del brigadista y el resto del coordinador."""
        ruta = request.path
        if not ruta.startswith("/api/") or ruta == "/api/salud" or ruta.startswith("/api/auth/"):
            return None
        if ruta.endswith("/verificar-sla"):
            return None  # la protege el secreto compartido con n8n (ver la ruta)
        g.usuario = usuario_actual()
        if not g.usuario:
            return {"error": "Inicie sesión para continuar."}, 401
        requerido = "brigadista" if ruta.startswith("/api/mi/") else "coordinador"
        if g.usuario.rol != requerido:
            return {"error": "Su rol no tiene acceso a esta sección."}, 403
        return None

    @app.get("/api/salud")
    def salud():
        return {"ok": True, "n8n": bool(os.getenv("N8N_WEBHOOK_URL"))}

    # ---- Autenticación por rol (coordinador | brigadista)
    @app.post("/api/auth/ingresar")
    def ingresar():
        datos = request.get_json(silent=True) or {}
        u = Usuario.query.filter_by(usuario=(datos.get("usuario") or "").strip().lower()).first()
        if not u or not u.verificar_clave(datos.get("clave") or ""):
            return {"error": "Usuario o contraseña incorrectos."}, 401
        session.clear()
        session["uid"] = u.id
        return _perfil(u)

    @app.post("/api/auth/salir")
    def salir():
        session.clear()
        return {"ok": True}

    @app.get("/api/auth/yo")
    def yo():
        u = usuario_actual()
        if not u:
            return {"error": "Sin sesión"}, 401
        return _perfil(u)

    # ---- Portal del brigadista
    @app.get("/api/mi/asignaciones")
    def mis_asignaciones():
        b = g.usuario.brigadista
        asignaciones = Asignacion.query.filter_by(brigadista_id=b.id).order_by(Asignacion.id.desc()).all()
        return {"brigadista": b.to_dict(), "asignaciones": [asignacion_para_brigadista(a) for a in asignaciones]}

    @app.post("/api/mi/asignaciones/<int:aid>/responder")
    def responder_asignacion(aid):
        a = db.session.get(Asignacion, aid)
        if not a or a.brigadista_id != g.usuario.brigadista_id:
            abort(404)
        acepta = bool((request.get_json(silent=True) or {}).get("acepta"))
        a, mensaje = M.registrar_respuesta(a.token, acepta, canal="el portal del brigadista")
        if mensaje != "ok":
            return {"error": mensaje}, 409
        return asignacion_para_brigadista(a)

    @app.get("/api/empresas")
    def empresas():
        return jsonify([e.to_dict() for e in EmpresaAfiliada.query.all()])

    @app.get("/api/incidentes")
    def incidentes():
        return jsonify([i.to_dict() for i in Incidente.query.order_by(Incidente.id.desc()).all()])

    @app.post("/api/incidentes")
    def crear_incidente():
        datos = request.get_json(force=True)
        faltan = [c for c in ("tipo", "lat", "lon", "municipio", "empresa_id") if datos.get(c) in (None, "")]
        if faltan:
            return {"error": f"Campos obligatorios faltantes: {', '.join(faltan)}"}, 400
        if datos["tipo"] not in M.R.CERT_REQUERIDA:
            return {"error": "Tipo de incidente no soportado"}, 400
        inc = M.registrar_y_despachar(datos, actor=datos.get("actor", "cliente"))
        return inc.to_dict(detalle=True), 201

    @app.post("/api/incidentes/previsualizar")
    def previsualizar():
        datos = request.get_json(force=True)
        if datos.get("tipo") not in M.R.CERT_REQUERIDA:
            return {"error": "Tipo de incidente no soportado"}, 400
        return M.previsualizar(datos)

    @app.get("/api/simulacion")
    def simulacion():
        """Resumen de resultados_simulacion.json (sección 6.8 del documento)."""
        ruta = os.path.join(os.path.dirname(__file__), "resultados_simulacion.json")
        if not os.path.exists(ruta):
            return {"disponible": False}
        with open(ruta, encoding="utf-8") as f:
            r = json.load(f)
        asis, tobe = r["asis"]["reporte_a_despacho_min"], r["tobe"]["reporte_a_brigada_confirmada_min"]
        return {"disponible": True, "n": r["n"],
                "asis_media": asis["media"], "asis_p90": asis["p90"],
                "tobe_media": tobe["media"], "tobe_p90": tobe["p90"],
                "sin_intervencion_pct": round(100 - r["tobe"]["escalados_a_coordinador_pct"], 1),
                "despacho_erroneo_asis_pct": r["asis"]["reproceso_pct"],
                "despacho_erroneo_tobe_pct": r["tobe"]["despacho_erroneo_pct"],
                "por_nivel": {n: {"asis": v["asis_media_min"]["media"], "tobe": v["tobe_media_min"]["media"]}
                              for n, v in r["por_nivel"].items()}}

    @app.get("/api/incidentes/<int:iid>")
    def detalle(iid):
        return db.get_or_404(Incidente, iid).to_dict(detalle=True)

    @app.get("/api/incidentes/<int:iid>/informe")
    def informe(iid):
        return M.informe(db.get_or_404(Incidente, iid))

    @app.post("/api/incidentes/<int:iid>/estado")
    def cambiar_estado(iid):
        inc = db.get_or_404(Incidente, iid)
        datos = request.get_json(force=True)
        try:
            M.avanzar_estado(inc, datos["estado"], datos.get("actor", "coordinador"), datos.get("notas"))
        except M.TransicionInvalida as e:
            return {"error": str(e)}, 409
        return inc.to_dict(detalle=True)

    @app.post("/api/incidentes/<int:iid>/verificar-sla")
    def verificar_sla(iid):
        # La invoca n8n con el secreto compartido, o el coordinador desde la consola ("forzar vencimiento").
        u = usuario_actual()
        if not (_secreto_ok() or (u and u.rol == "coordinador")):
            abort(401)
        forzar = bool((request.get_json(silent=True) or {}).get("forzar"))
        return M.verificar_sla(db.get_or_404(Incidente, iid), forzar=forzar)

    @app.get("/api/brigadistas")
    def brigadistas():
        return jsonify([b.to_dict() for b in Brigadista.query.order_by(Brigadista.base, Brigadista.nombre).all()])

    @app.patch("/api/brigadistas/<int:bid>")
    def actualizar_brigadista(bid):
        b = db.get_or_404(Brigadista, bid)
        b.estado = request.get_json(force=True)["estado"]
        db.session.commit()
        return b.to_dict()

    @app.get("/api/equipos")
    def equipos():
        return jsonify([e.to_dict() for e in Equipo.query.order_by(Equipo.base, Equipo.tipo).all()])

    @app.patch("/api/equipos/<int:eid>")
    def actualizar_equipo(eid):
        e = db.get_or_404(Equipo, eid)
        e.estado = request.get_json(force=True)["estado"]
        db.session.commit()
        return e.to_dict()

    @app.get("/api/kpis")
    def kpis():
        return calcular_kpis()

    @app.get("/api/notificaciones")
    @app.get("/api/notificaciones-simuladas", endpoint="bandeja_anterior")  # nombre anterior
    def bandeja():
        return jsonify(notificador.BANDEJA[:30])

    @app.post("/api/demo/reiniciar")
    def reiniciar():
        semilla.cargar()
        notificador.BANDEJA.clear()
        return {"ok": True}

    # ---- Página móvil de confirmación del brigadista (enlace del correo / SMS; no exige sesión).
    #      Plantilla: templates/confirmar.html
    @app.route("/confirmar/<token>", methods=["GET", "POST"])
    def confirmar(token):
        a = Asignacion.query.filter_by(token=token).first_or_404()
        if request.method == "POST" or request.args.get("respuesta") == "no":
            acepta = request.form.get("respuesta", request.args.get("respuesta", "si")) == "si"
            _, mensaje = M.registrar_respuesta(token, acepta)
            # Post/Redirect/Get: recargar la página no reenvía la respuesta
            return redirect(f"/confirmar/{token}?resultado={'ok' if mensaje == 'ok' else 'ya'}", code=303)
        return render_template("confirmar.html", a=a, inc=a.incidente, resultado=request.args.get("resultado"),
                               fuentes=fuentes_de_la_app(),
                               vence_en=a.vence_en(), ahora=M.ahora(),
                               sla=M.R.SLA_CONFIRMACION_MIN.get(a.incidente.nivel or 1, 5))

    # ---- Frontend React compilado
    @app.get("/", defaults={"ruta": ""})
    @app.get("/<path:ruta>")
    def frontend(ruta):
        if ruta.startswith("api/"):
            abort(404)
        if ruta and os.path.exists(os.path.join(DIST, ruta)):
            return send_from_directory(DIST, ruta)
        if os.path.exists(os.path.join(DIST, "index.html")):
            return send_from_directory(DIST, "index.html")
        return "Frontend no compilado. Ejecute 'npm run build' en /frontend o use 'npm run dev'.", 200


def calcular_kpis():
    incs = Incidente.query.all()
    asig = Asignacion.query.all()
    notif = [i.segundos("reportado_en", "notificado_en") for i in incs if i.notificado_en]
    conf = [i.segundos("reportado_en", "confirmado_en") for i in incs if i.confirmado_en]
    cerrados = [i for i in incs if i.estado == "cerrado"]
    tipos_req = {"REPORTE", "CLASIFICACION", "ASIGNACION", "NOTIFICACION", "CIERRE", "INFORME"}
    trazables = [i for i in cerrados if tipos_req <= {e.tipo for e in i.eventos}]
    reasig = [a for a in asig if a.estado in ("vencido", "rechazado")]  # no_requerido no cuenta
    brig = Brigadista.query.all()
    eq = Equipo.query.all()
    return {
        "incidentes_totales": len(incs),
        "incidentes_activos": sum(1 for i in incs if i.estado != "cerrado"),
        "seg_prom_reporte_a_notificacion": round(mean(notif), 3) if notif else None,
        "min_prom_reporte_a_brigada_confirmada": round(mean(conf) / 60, 3) if conf else None,
        "tasa_reasignacion_pct": round(100 * len(reasig) / len(asig), 1) if asig else 0,
        "incidentes_con_escalamiento_pct": round(100 * sum(1 for i in incs if i.rondas_escalamiento) / len(incs), 1) if incs else 0,
        "trazabilidad_completa_pct": round(100 * len(trazables) / len(cerrados), 1) if cerrados else None,
        "brigadistas_disponibles": sum(1 for b in brig if b.estado == "disponible"),
        "brigadistas_totales": len(brig),
        "equipos_disponibles": sum(1 for e in eq if e.estado == "disponible"),
        "equipos_totales": len(eq),
    }


def vigilante_sla(app, intervalo=20):
    """Respaldo del temporizador de n8n: revisa SLA vencidos periódicamente."""
    while True:
        time.sleep(intervalo)
        with app.app_context():
            for inc in Incidente.query.filter_by(estado="notificado").all():
                M.verificar_sla(inc)


if __name__ == "__main__":
    aplicacion = crear_app()
    if os.getenv("VIGILANTE_SLA", "1") == "1":
        threading.Thread(target=vigilante_sla, args=(aplicacion,), daemon=True).start()
    aplicacion.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
