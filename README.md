# MVP — Despacho automatizado de brigadas ante contingencias ambientales (ARKOF S.A.S.)

Proyecto académico del curso **Gerencia de Operaciones de TI** (Universidad de La Sabana, 2026-2).
Equipo: Darek Aljuri Martínez, Valentina Ruiz Torres, Santiago Soler Prado.

Link Video demostrativo: https://www.youtube.com/watch?v=wSBJssc8Row

> Todos los datos (brigadistas, empresas, teléfonos, correos) son **ficticios**. Los umbrales de las
> reglas de negocio son **supuestos** del equipo, pendientes de validación con ARKOF (`backend/reglas.py`).

Este repositorio es el entregable del **capítulo 8 (MVP funcional)** del documento del proyecto: código fuente,
flujo de automatización de n8n, configuración, pruebas automatizadas y simulación AS-IS vs. TO-BE.

## Inicio rápido (modo simulación, sin n8n)

Requiere Python 3.10+. El frontend ya viene compilado en `frontend/dist`, así que no hace falta Node.js.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python app.py                      # http://localhost:5000
```

Ingrese con la cuenta **`coordinador`**. La contraseña de las cuentas de demostración es la de `CLAVE_DEMO`
en `backend/.env` o, si no se define, la de `CLAVE_DEMO_POR_DEFECTO` en `backend/semilla.py`. En modo
simulación los avisos no salen a n8n: se ven en la vista **Notificaciones**, con sus enlaces de confirmación.

## 1. Qué hace

Automatiza el proceso TO-BE del capítulo 6 del documento:

1. El coordinador registra el incidente (reporte del cliente o llamada) en la consola. Mientras escribe, la
   casilla 9 calcula el nivel, la brigada, la certificación, el plazo y el kit con las mismas reglas del motor.
2. El motor clasifica (nivel 1 a 3), selecciona la brigada más cercana con la certificación requerida, reserva
   el kit de la base más cercana y publica un evento a n8n.
3. n8n avisa a cada brigadista con un enlace móvil de confirmación y espera el plazo (nodo *Wait*).
4. Al vencer el plazo, n8n consulta la API: el motor reemplaza solo el déficit o escala al coordinador.
5. El coordinador sigue el incidente hasta el cierre; el sistema libera recursos y envía el informe al cliente.

### Usuarios y roles

| Rol | Qué ve | Cuenta de demostración |
|---|---|---|
| Coordinador (administrador) | Consola: tablero, reporte, detalle con bitácora, brigadistas y equipos, notificaciones | `coordinador` |
| Brigadista | Portal móvil: convocatorias con cuenta regresiva, confirmar o rechazar, brigada y kit del despacho en curso, historial | `nombre.apellido` sin tildes (p. ej. `paola.diaz`) |

El enlace que recibe el brigadista (`/confirmar/<token>`) funciona **sin iniciar sesión**, por la conectividad
limitada en campo (sección 6.4 del documento); el portal es un canal adicional.

### Canales de notificación

| Canal | Estado en el MVP |
|---|---|
| Correo (SMTP, Gmail) | Activo, validado con envíos reales |
| Telegram (bot) | **Canal de demostración**, activo: permite mostrar el aviso llegando al celular |
| SMS (Twilio) | Configurado en el flujo pero **desactivado**: la cuenta gratuita de Twilio no envía a Colombia; se activa con plan pago |

## 2. Arquitectura del MVP

```
Navegador (React) ──HTTP──> Flask API + motor de despacho ──SQLAlchemy──> SQLite (MVP) / PostgreSQL (prod.)
                                   │  ▲
                        webhook    │  │ POST /api/incidentes/<id>/verificar-sla  (X-ARKOF-Token)
                                   ▼  │
                                  n8n ──> SMTP (correo) · Telegram (demostración) · Twilio (SMS, producción)
```

La aplicación **no envía mensajes directamente**: publica eventos a n8n, que los convierte en correo, Telegram
o SMS (decisión de diseño del capítulo 7.3).

| Ruta | Contenido |
|---|---|
| `backend/app.py` | API REST, autenticación por rol, portal del brigadista, KPIs, temporizador de respaldo; sirve el frontend |
| `backend/motor_despacho.py` | Motor: clasificación, selección, reserva, notificación, confirmación, déficit, escalamiento y cierre |
| `backend/reglas.py` | Parámetros de las reglas RN-01 a RN-11 (archivo de configuración del dueño del proceso) |
| `backend/models.py`, `notificador.py`, `semilla.py` | Modelo de datos, integración con n8n y datos ficticios de demostración |
| `backend/templates/confirmar.html` | Página móvil del enlace de confirmación |
| `backend/tests/` | 35 pruebas automatizadas (pytest) |
| `backend/simular_escenarios.py`, `demo_escenarios.py` | Simulación AS-IS vs. TO-BE y carga de 3 incidentes de demostración |
| `frontend/src/` | React 18 + Vite: ingreso por rol, consola del coordinador (`Consola.jsx`) y portal del brigadista (`Portal.jsx`) |
| `frontend/dist/` | Frontend compilado (lo sirve Flask) |
| `n8n/arkof_despacho_workflow.json` | Flujo de n8n importable (13 nodos) |
| `n8n/iniciar_n8n.mjs`, `n8n/enlazar_credenciales.py` | Arrancar, importar y activar n8n local; enlazar credenciales a los nodos |
| `docs/` | Diagramas del documento, capturas del MVP (`docs/capturas`) y resultados de la simulación |
| `PRODUCT.md`, `DESIGN.md` | Contexto de producto y sistema visual de la interfaz |

## 3. Ejecución completa (con n8n, correo y Telegram)

Requisitos adicionales: Node.js 20+ (n8n se ejecuta con `npx`, sin instalación global).

```bash
node n8n/iniciar_n8n.mjs importar   # importa o actualiza el flujo (id fijo, no se duplica)
node n8n/iniciar_n8n.mjs activar    # lo deja activo
node n8n/iniciar_n8n.mjs            # inicia n8n en http://localhost:5678
```

1. En `http://localhost:5678/setup` cree la cuenta de n8n (solo la primera vez).
2. En n8n, *Credentials → Create credential*: **SMTP** (Gmail: `smtp.gmail.com`, puerto 465, SSL, contraseña de
   aplicación), **Telegram API** (token del bot creado con @BotFather) y, si hay plan pago, **Twilio**.
3. En `backend/.env`: `N8N_WEBHOOK_URL=http://localhost:5678/webhook/arkof-despacho`, `VIGILANTE_SLA=0`,
   `ARKOF_CORREO_REMITENTE` (el mismo Gmail de la credencial), `DEMO_TELEGRAM_CHAT_ID` (su Id, que da @userinfobot)
   y, opcionalmente, `DEMO_EMAIL` para recibir todos los avisos en un solo correo.
4. Con n8n detenido, enlace las credenciales a los nodos y reimporte:
   `python n8n/enlazar_credenciales.py`, luego `node n8n/iniciar_n8n.mjs importar n8n/.flujo_enlazado.json`
   y `node n8n/iniciar_n8n.mjs activar`. Inicie n8n y la app.

**Acceso desde el celular u otro equipo.** Exponga la app con un túnel (`ngrok http 5000`, requiere cuenta
gratuita de ngrok) y copie la URL `https://…` en `PUBLIC_BASE_URL`; así los enlaces del correo y de Telegram
abren desde el teléfono. Con un enlace público, defina `CLAVE_DEMO` y `SECRET_KEY` propias antes de crear la base.

**n8n Cloud.** Importe el JSON con *Import from file*, asigne las credenciales, active el flujo y copie la
*Production URL* del webhook en `N8N_WEBHOOK_URL`. Como n8n Cloud no tiene variables de entorno propias, escriba
el secreto compartido en el encabezado `X-ARKOF-Token` del nodo *Verificar plazo en la API*.

### Variables de entorno (`backend/.env`, ver `.env.example`)

| Variable | Uso |
|---|---|
| `N8N_WEBHOOK_URL` | URL de producción del webhook de n8n. Vacía = modo simulación |
| `N8N_SHARED_SECRET` | Secreto compartido; n8n lo envía en `X-ARKOF-Token` al verificar el plazo |
| `PUBLIC_BASE_URL` | URL pública de la app (aparece en los enlaces de los avisos) |
| `COORDINADOR_EMAIL`, `COORDINADOR_TELEFONO` | Destino de las alertas al coordinador |
| `VIGILANTE_SLA` | `1` = temporizador interno de respaldo; `0` cuando n8n está activo |
| `SLA_DEMO_MIN` | Acorta el plazo de confirmación para demostraciones (p. ej. `1`); sin ella rige RN-07 (5 / 5 / 4 min) |
| `DEMO_EMAIL`, `DEMO_TELEFONO` | Redirigen todos los avisos a un correo y un celular reales (borrar `backend/instance/*.db` al cambiarlos) |
| `DEMO_TELEGRAM_CHAT_ID` | Chat de Telegram que recibe los avisos de demostración |
| `SECRET_KEY` | Firma la cookie de sesión |
| `CLAVE_DEMO` | Contraseña de las cuentas de demostración (se aplica al crear la base) |
| `TWILIO_FROM_NUMBER`, `ARKOF_CORREO_REMITENTE` | Las lee n8n: número remitente de Twilio y *From* de los correos |
| `DATABASE_URL` | Por defecto SQLite; en producción, PostgreSQL |

## 4. Pruebas

```bash
cd backend
python -m pytest -q                 # 35 pruebas: reglas RN-01 a RN-11, acceso por rol, portal, enlace y canales
python demo_escenarios.py           # con la app corriendo: carga 3 incidentes de demostración
python simular_escenarios.py 300    # simulación AS-IS vs. TO-BE (semilla 2026) → resultados_simulacion.json
```

Las pruebas no leen `backend/.env` (`tests/conftest.py`): nunca publican en n8n ni envían mensajes reales.

Prueba funcional manual (guion del video):

0. Ingresar como `coordinador`; en otra ventana o en el celular, ingresar como un brigadista.
1. *Reportar incidente* → derrame, Acacías, 3 barriles: la casilla 9 anticipa nivel, brigada y kit; al
   registrar, la bitácora muestra la clasificación, la brigada, la reserva y la notificación en milisegundos.
2. En el detalle, pulsar **Rechaza** en un brigadista → la bitácora muestra el reemplazo (RN-08).
3. Pulsar **Forzar vencimiento del plazo** → reemplazo automático de quienes no respondieron.
4. Confirmar el resto (desde el enlace, el portal o el detalle) → *Brigada confirmada*; avanzar estados y
   **Cerrar** → informe de trazabilidad.
5. Con n8n activo, dejar vencer el plazo sin responder para ver el reemplazo disparado por n8n.

## 5. API principal

| Método | Ruta | Descripción |
|---|---|---|
| POST / GET | `/api/auth/ingresar`, `/api/auth/salir`, `/api/auth/yo` | Sesión por rol (cookie firmada) |
| POST | `/api/incidentes` | Reporta y despacha (empresa_id, tipo, municipio, lat, lon, volumen_bbl, cuerpo_agua, comunidad_cercana) |
| POST | `/api/incidentes/previsualizar` | Aplica las reglas sin registrar (casilla 9) |
| GET | `/api/incidentes`, `/api/incidentes/<id>` | Lista y detalle con asignaciones, equipos y bitácora |
| POST | `/api/incidentes/<id>/estado` | Avanza el ciclo de vida (`en_ruta`, `en_sitio`, `controlado`, `cerrado` + notas) |
| POST | `/api/incidentes/<id>/verificar-sla` | La invoca n8n (secreto compartido) o el coordinador |
| GET | `/api/kpis`, `/api/simulacion` | Indicadores del tablero y resumen de la simulación |
| GET / PATCH | `/api/brigadistas`, `/api/equipos` | Disponibilidad de personal y equipos |
| GET | `/api/notificaciones` | Eventos publicados, con sus enlaces |
| GET | `/api/mi/asignaciones` | Portal del brigadista: sus asignaciones |
| POST | `/api/mi/asignaciones/<id>/responder` | El brigadista confirma o rechaza (`{"acepta": true}`) |
| GET / POST | `/confirmar/<token>` | Página móvil del enlace (sin sesión) |

Toda la API exige sesión salvo `/api/salud`, `/api/auth/*` y `verificar-sla`. `/api/mi/*` es del brigadista;
el resto, del coordinador.

## 6. Limitaciones conocidas del MVP

Distancias en línea recta (no rutas viales); autenticación básica con usuario y contraseña (sin recuperación
de clave, bloqueo por intentos ni rol de gerencia); la empresa afiliada no tiene cuenta propia (su reporte lo
registra el coordinador); SQLite y ejecución local, con acceso remoto por túnel; SMS desactivado hasta contar
con plan pago de Twilio. Estas brechas se abordan en la arquitectura objetivo del capítulo 7.
