"""Datos de demostración. TODOS los nombres, teléfonos y correos son FICTICIOS.
ARKOF no compartió datos reales de su personal ni de sus clientes (confidenciales)."""
import os
import unicodedata

from models import db, EmpresaAfiliada, Brigadista, Equipo, Usuario

# Cuentas de demostración: usuario "coordinador" y uno por brigadista (nombre.apellido, sin tildes).
# La clave es la misma para todas y se cambia con CLAVE_DEMO en backend/.env. Es un dato de prueba,
# no una credencial real: los brigadistas son ficticios.
CLAVE_DEMO_POR_DEFECTO = "arkof2026"


def nombre_usuario(nombre):
    plano = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return ".".join(plano.lower().split())

BASES = {
    "Villavicencio": (4.1420, -73.6266),
    "Acacías": (3.9869, -73.7590),
    "Puerto Gaitán": (4.3136, -72.0824),
    "Yopal": (5.3378, -72.3959),
}

EMPRESAS = [
    ("Petro Llanos S.A.S. (ficticia)", "Hidrocarburos", "hse@petrollanos.example"),
    ("Palmas del Meta S.A. (ficticia)", "Agroindustrial", "ambiental@palmasmeta.example"),
    ("Químicos Orinoquía Ltda. (ficticia)", "Industrial", "seguridad@quimicosori.example"),
]

# nombre, rol, certificaciones, base
BRIGADISTAS = [
    ("Andrés Rojas", "lider", "ANTIDERRAME,HAZMAT,PRIMEROS_AUXILIOS", "Villavicencio"),
    ("Paola Díaz", "lider", "ANTIDERRAME,PRIMEROS_AUXILIOS", "Acacías"),
    ("Jhon Castro", "lider", "HAZMAT,ANTIDERRAME", "Puerto Gaitán"),
    ("Luisa Mejía", "lider", "ANTIDERRAME,HAZMAT", "Yopal"),
    ("Camilo Ortiz", "tecnico", "ANTIDERRAME", "Villavicencio"),
    ("Diana Parra", "tecnico", "ANTIDERRAME,HAZMAT", "Villavicencio"),
    ("Óscar Gómez", "tecnico", "ANTIDERRAME", "Villavicencio"),
    ("Yeison Vargas", "tecnico", "HAZMAT", "Acacías"),
    ("Karen Suárez", "tecnico", "ANTIDERRAME,PRIMEROS_AUXILIOS", "Acacías"),
    ("Wilmer Rincón", "tecnico", "ANTIDERRAME", "Puerto Gaitán"),
    ("Natalia León", "tecnico", "ANTIDERRAME,HAZMAT", "Puerto Gaitán"),
    ("Edwin Pardo", "tecnico", "ANTIDERRAME", "Yopal"),
    ("Sandra Beltrán", "tecnico", "HAZMAT,ANTIDERRAME", "Yopal"),
    ("Julián Torres", "tecnico", "ANTIDERRAME", "Villavicencio"),
]

# tipo, cantidad por base, descripción
ABREV = {"KIT_ANTIDERRAME": "KAD", "BARRERA": "BAR", "ABSORBENTE": "ABS",
         "KIT_HAZMAT": "KHZ", "EPP": "EPP", "VEHICULO": "VEH"}

INVENTARIO = [
    ("KIT_ANTIDERRAME", 2, "Kit antiderrames 120 L"),
    ("BARRERA", 2, "Barrera de contención 25 m"),
    ("ABSORBENTE", 3, "Paca de material absorbente"),
    ("KIT_HAZMAT", 1, "Kit HAZMAT de respuesta"),
    ("EPP", 6, "Juego EPP (traje, guantes, respirador)"),
    ("VEHICULO", 1, "Camioneta 4x4 de respuesta"),
]


def cargar():
    db.drop_all()
    db.create_all()
    for n, s, e in EMPRESAS:
        db.session.add(EmpresaAfiliada(nombre=n, sector=s, contacto_email=os.getenv("DEMO_EMAIL") or e,
                                       contacto_telefono="+570000000000"))
    for i, (n, rol, certs, base) in enumerate(BRIGADISTAS, start=1):
        lat, lon = BASES[base]
        db.session.add(Brigadista(nombre=n, rol=rol, certificaciones=certs, base=base, lat=lat, lon=lon,
                                  telefono=os.getenv("DEMO_TELEFONO") or f"+57300000{i:04d}",
                                  email=os.getenv("DEMO_EMAIL") or f"brigadista{i:02d}@arkof.example"))
    for base in BASES:
        pref = base[:3].upper().replace("Í", "I")
        for tipo, cant, desc in INVENTARIO:
            for k in range(1, cant + 1):
                db.session.add(Equipo(codigo=f"{pref}-{ABREV[tipo]}-{k:02d}", tipo=tipo, descripcion=desc,
                                      base=base, estado="disponible"))
    db.session.commit()
    crear_cuentas()


def crear_cuentas():
    """Crea la cuenta del coordinador y una por brigadista que aún no la tenga (p. ej., bases anteriores al login)."""
    # Todas las cuentas de demo comparten clave, así que el hash se calcula una sola vez
    # (cada hash cuesta ~80 ms y la semilla se recarga en cada prueba y al reiniciar la demo).
    plantilla = Usuario()
    plantilla.fijar_clave(os.getenv("CLAVE_DEMO") or CLAVE_DEMO_POR_DEFECTO)
    if not Usuario.query.filter_by(usuario="coordinador").first():
        db.session.add(Usuario(usuario="coordinador", nombre="Coordinación HSE", rol="coordinador",
                               clave_hash=plantilla.clave_hash))
    for b in Brigadista.query.all():
        if not b.usuario:
            db.session.add(Usuario(usuario=nombre_usuario(b.nombre), nombre=b.nombre, rol="brigadista",
                                   brigadista=b, clave_hash=plantilla.clave_hash))
    db.session.commit()
