"""Reglas de negocio parametrizables (RN-01 a RN-11 del capítulo 6.6).

IMPORTANTE: los umbrales numéricos son SUPUESTOS del equipo del proyecto,
construidos para el MVP académico. Deben validarse con el coordinador HSE de
ARKOF antes de cualquier uso real. Se centralizan aquí para que el dueño del
proceso pueda ajustarlos sin modificar la lógica del motor.
"""
import os

# RN-01 Clasificación de severidad -------------------------------------------
UMBRAL_VOLUMEN_NIVEL2_BBL = 5     # >= 5 barriles => al menos nivel 2
UMBRAL_VOLUMEN_NIVEL3_BBL = 50    # >= 50 barriles => nivel 3
TIPOS_PELIGROSOS = {"SUSTANCIA_NOCIVA", "FUGA_GAS"}  # elevan un nivel mínimo 2

# RN-02 Composición de la brigada por nivel ----------------------------------
TAMANO_BRIGADA = {1: 2, 2: 4, 3: 6}
LIDERES_REQUERIDOS = {1: 1, 2: 1, 3: 2}

# RN-03 Certificaciones exigidas por tipo de incidente ------------------------
CERT_REQUERIDA = {
    "DERRAME_HIDROCARBURO": "ANTIDERRAME",
    "SUSTANCIA_NOCIVA": "HAZMAT",
    "FUGA_GAS": "HAZMAT",
}

# RN-05 Kit de equipos por tipo y nivel: {tipo_equipo: cantidad}
KIT_EQUIPOS = {
    "DERRAME_HIDROCARBURO": {1: {"KIT_ANTIDERRAME": 1, "ABSORBENTE": 1, "EPP": 2},
                             2: {"KIT_ANTIDERRAME": 1, "BARRERA": 1, "ABSORBENTE": 2, "EPP": 4},
                             3: {"KIT_ANTIDERRAME": 2, "BARRERA": 2, "ABSORBENTE": 3, "EPP": 6}},
    "SUSTANCIA_NOCIVA": {1: {"KIT_HAZMAT": 1, "EPP": 2},
                         2: {"KIT_HAZMAT": 1, "ABSORBENTE": 1, "EPP": 4},
                         3: {"KIT_HAZMAT": 2, "ABSORBENTE": 2, "EPP": 6}},
    "FUGA_GAS": {1: {"KIT_HAZMAT": 1, "EPP": 2},
                 2: {"KIT_HAZMAT": 1, "EPP": 4},
                 3: {"KIT_HAZMAT": 2, "EPP": 6}},
}

# RN-06 Vehículos: 1 vehículo 4x4 por cada 4 brigadistas (redondeo hacia arriba)
BRIGADISTAS_POR_VEHICULO = 4

# RN-07 Tiempo máximo de confirmación (SLA) por nivel, en minutos
SLA_CONFIRMACION_MIN = {1: 5, 2: 5, 3: 4}
# Para demostraciones en vivo o grabación del video se puede acortar el plazo:
#   SLA_DEMO_MIN=1  (aplica a todos los niveles)
if os.getenv("SLA_DEMO_MIN"):
    SLA_CONFIRMACION_MIN = {n: float(os.getenv("SLA_DEMO_MIN")) for n in (1, 2, 3)}

# RN-07b Sobre-convocatoria: técnicos adicionales notificados en paralelo por nivel.
# Los primeros en confirmar completan la brigada; los sobrantes se liberan.
SOBRECONVOCATORIA = {1: 0, 2: 1, 3: 2}

# RN-08 Rondas máximas de escalamiento automático antes de pasar a decisión humana
MAX_RONDAS_ESCALAMIENTO = 2

# RN-04 Control de fatiga: quien acumula este número de atenciones cerradas en las últimas
# VENTANA_FATIGA_HORAS pasa al final del orden de convocatoria. No se excluye: si no hay alternativa
# se le convoca igual y el sistema alerta al coordinador para que decida.
MAX_ATENCIONES_24H = 2
VENTANA_FATIGA_HORAS = 24

# Ciclo de vida permitido del incidente (RN-11: toda transición queda en bitácora)
TRANSICIONES = {
    "reportado": {"notificado", "cerrado"},
    "notificado": {"confirmado", "cerrado"},
    "confirmado": {"en_ruta", "cerrado"},
    "en_ruta": {"en_sitio", "cerrado"},
    "en_sitio": {"controlado", "cerrado"},
    "controlado": {"cerrado"},
    "cerrado": set(),
}
