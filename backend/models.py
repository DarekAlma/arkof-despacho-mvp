"""Modelo de datos del MVP de despacho de brigadas (ARKOF S.A.S.).

Entidades principales:
- EmpresaAfiliada: cliente con convenio de ayuda mutua que reporta incidentes.
- Brigadista: personal de campo con certificaciones, base y estado.
- Equipo: recursos físicos (kits, barreras, EPP, vehículos) con estado.
- Incidente: contingencia ambiental reportada; eje del proceso.
- Asignacion: vínculo brigadista-incidente con token de confirmación.
- ReservaEquipo: vínculo equipo-incidente.
- Evento: bitácora inmutable de trazabilidad (quién, qué, cuándo).
- Usuario: cuenta de acceso con rol (coordinador | brigadista).
"""
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

import reglas as R

db = SQLAlchemy()


def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class EmpresaAfiliada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    sector = db.Column(db.String(60))
    contacto_email = db.Column(db.String(120))
    contacto_telefono = db.Column(db.String(30))

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "sector": self.sector,
                "contacto_email": self.contacto_email}


class Brigadista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    rol = db.Column(db.String(30), default="tecnico")  # lider | tecnico
    certificaciones = db.Column(db.String(200), default="")  # CSV: HAZMAT,ANTIDERRAME,PRIMEROS_AUXILIOS
    telefono = db.Column(db.String(30))
    email = db.Column(db.String(120))
    base = db.Column(db.String(60))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    estado = db.Column(db.String(20), default="disponible")  # disponible | asignado | fuera_turno | incapacitado
    atenciones_24h = db.Column(db.Integer, default=0)  # obsoleto: la carga se calcula con atenciones_recientes()

    def atenciones_recientes(self, horas=None):
        """RN-04: atenciones de este brigadista (brigada confirmada) en incidentes cerrados dentro de la ventana."""
        desde = ahora() - timedelta(hours=horas or R.VENTANA_FATIGA_HORAS)
        return (Asignacion.query.join(Incidente)
                .filter(Asignacion.brigadista_id == self.id, Asignacion.estado == "confirmado",
                        Incidente.cerrado_en.isnot(None), Incidente.cerrado_en >= desde)
                .count())

    def certs(self):
        return {c.strip() for c in (self.certificaciones or "").split(",") if c.strip()}

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "rol": self.rol,
                "certificaciones": sorted(self.certs()), "telefono": self.telefono,
                "email": self.email, "base": self.base, "estado": self.estado,
                "atenciones_24h": self.atenciones_recientes(),
                "usuario": self.usuario.usuario if self.usuario else None}


class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True)
    tipo = db.Column(db.String(40))  # KIT_ANTIDERRAME | BARRERA | ABSORBENTE | KIT_HAZMAT | EPP | VEHICULO
    descripcion = db.Column(db.String(160))
    base = db.Column(db.String(60))
    estado = db.Column(db.String(20), default="disponible")  # disponible | reservado | mantenimiento

    def to_dict(self):
        return {"id": self.id, "codigo": self.codigo, "tipo": self.tipo,
                "descripcion": self.descripcion, "base": self.base, "estado": self.estado}


class Usuario(db.Model):
    """Cuenta de acceso. El coordinador opera la consola; el brigadista solo ve sus asignaciones."""
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(60), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    clave_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # coordinador | brigadista
    brigadista_id = db.Column(db.Integer, db.ForeignKey("brigadista.id"))
    brigadista = db.relationship("Brigadista", backref=db.backref("usuario", uselist=False))

    def fijar_clave(self, clave):
        self.clave_hash = generate_password_hash(clave)

    def verificar_clave(self, clave):
        return check_password_hash(self.clave_hash, clave)

    def to_dict(self):
        return {"id": self.id, "usuario": self.usuario, "nombre": self.nombre, "rol": self.rol,
                "brigadista_id": self.brigadista_id}


class Incidente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresa_afiliada.id"))
    empresa = db.relationship("EmpresaAfiliada")
    tipo = db.Column(db.String(40))  # DERRAME_HIDROCARBURO | SUSTANCIA_NOCIVA | FUGA_GAS
    descripcion = db.Column(db.Text)
    municipio = db.Column(db.String(60))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    volumen_bbl = db.Column(db.Float, default=0)
    cuerpo_agua = db.Column(db.Boolean, default=False)
    comunidad_cercana = db.Column(db.Boolean, default=False)
    nivel = db.Column(db.Integer)  # 1, 2, 3
    estado = db.Column(db.String(20), default="reportado")
    canal = db.Column(db.String(20), default="portal")  # portal | telefono | coordinador
    rondas_escalamiento = db.Column(db.Integer, default=0)
    recursos_insuficientes = db.Column(db.Boolean, default=False)
    notas_cierre = db.Column(db.Text)
    reportado_en = db.Column(db.DateTime, default=ahora)
    asignado_en = db.Column(db.DateTime)
    notificado_en = db.Column(db.DateTime)
    confirmado_en = db.Column(db.DateTime)
    en_sitio_en = db.Column(db.DateTime)
    cerrado_en = db.Column(db.DateTime)

    asignaciones = db.relationship("Asignacion", back_populates="incidente", cascade="all, delete-orphan")
    reservas = db.relationship("ReservaEquipo", back_populates="incidente", cascade="all, delete-orphan")
    eventos = db.relationship("Evento", back_populates="incidente", order_by="Evento.id",
                              cascade="all, delete-orphan")

    def segundos(self, a, b):
        ta, tb = getattr(self, a), getattr(self, b)
        return (tb - ta).total_seconds() if ta and tb else None

    def to_dict(self, detalle=False):
        d = {"id": self.id, "codigo": self.codigo, "tipo": self.tipo,
             "empresa": self.empresa.nombre if self.empresa else None,
             "municipio": self.municipio, "nivel": self.nivel, "estado": self.estado,
             "volumen_bbl": self.volumen_bbl, "cuerpo_agua": self.cuerpo_agua,
             "comunidad_cercana": self.comunidad_cercana, "canal": self.canal,
             "rondas_escalamiento": self.rondas_escalamiento,
             "recursos_insuficientes": self.recursos_insuficientes,
             "reportado_en": _iso(self.reportado_en), "asignado_en": _iso(self.asignado_en),
             "notificado_en": _iso(self.notificado_en), "confirmado_en": _iso(self.confirmado_en),
             "en_sitio_en": _iso(self.en_sitio_en), "cerrado_en": _iso(self.cerrado_en),
             "seg_reporte_a_notificacion": self.segundos("reportado_en", "notificado_en"),
             "seg_reporte_a_confirmacion": self.segundos("reportado_en", "confirmado_en"),
             "sla_minutos": R.SLA_CONFIRMACION_MIN.get(self.nivel or 1, 5),
             "brigada_requerida": R.TAMANO_BRIGADA.get(self.nivel or 1),
             "convocado_con_fatiga": any(e.tipo == "CONVOCATORIA_CON_FATIGA" for e in self.eventos)}
        if detalle:
            d.update({"descripcion": self.descripcion, "lat": self.lat, "lon": self.lon,
                      "notas_cierre": self.notas_cierre,
                      "asignaciones": [a.to_dict() for a in self.asignaciones],
                      "equipos": [r.equipo.to_dict() | {"liberado": r.liberado} for r in self.reservas],
                      "eventos": [e.to_dict() for e in self.eventos]})
        return d


class Asignacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incidente_id = db.Column(db.Integer, db.ForeignKey("incidente.id"))
    incidente = db.relationship("Incidente", back_populates="asignaciones")
    brigadista_id = db.Column(db.Integer, db.ForeignKey("brigadista.id"))
    brigadista = db.relationship("Brigadista")
    rol_en_brigada = db.Column(db.String(20))
    token = db.Column(db.String(64), unique=True)
    estado = db.Column(db.String(20), default="pendiente")  # pendiente | confirmado | rechazado | vencido
    distancia_km = db.Column(db.Float)
    notificado_en = db.Column(db.DateTime)
    respondido_en = db.Column(db.DateTime)

    def vence_en(self):
        """Momento en que vence el plazo de confirmación (RN-07)."""
        if not self.notificado_en or not self.incidente or not self.incidente.nivel:
            return None
        return self.notificado_en + timedelta(minutes=R.SLA_CONFIRMACION_MIN[self.incidente.nivel])

    def to_dict(self):
        return {"id": self.id, "brigadista": self.brigadista.nombre, "brigadista_id": self.brigadista_id,
                "rol_en_brigada": self.rol_en_brigada, "estado": self.estado,
                "distancia_km": round(self.distancia_km or 0, 1), "token": self.token,
                "notificado_en": _iso(self.notificado_en), "respondido_en": _iso(self.respondido_en),
                "vence_en": _iso(self.vence_en())}


class ReservaEquipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incidente_id = db.Column(db.Integer, db.ForeignKey("incidente.id"))
    incidente = db.relationship("Incidente", back_populates="reservas")
    equipo_id = db.Column(db.Integer, db.ForeignKey("equipo.id"))
    equipo = db.relationship("Equipo")
    liberado = db.Column(db.Boolean, default=False)


class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incidente_id = db.Column(db.Integer, db.ForeignKey("incidente.id"))
    incidente = db.relationship("Incidente", back_populates="eventos")
    momento = db.Column(db.DateTime, default=ahora)
    actor = db.Column(db.String(60))  # sistema | n8n | coordinador | brigadista:<id> | cliente
    tipo = db.Column(db.String(40))
    detalle = db.Column(db.Text)

    def to_dict(self):
        return {"id": self.id, "momento": _iso(self.momento), "actor": self.actor,
                "tipo": self.tipo, "detalle": self.detalle}


def _iso(dt):
    return dt.isoformat() + "Z" if dt else None
