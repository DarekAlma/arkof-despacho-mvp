# CLAUDE.md — MVP de despacho de brigadas ARKOF S.A.S.

> Contexto para Claude Code. Vive en la raíz del repositorio para que se cargue en cada sesión.

## 1. Qué es este proyecto

MVP académico del curso **Gerencia de Operaciones de TI** (Universidad de La Sabana, 2026-2, docente
Mateo Barón Rojas). Equipo: Darek Aljuri Martínez, Valentina Ruiz Torres y Santiago Soler Prado.

Automatiza la **gestión y despacho de brigadas ante contingencias ambientales** (derrames de
hidrocarburos, sustancias nocivas, fugas de gas) de ARKOF S.A.S., empresa de Villavicencio (Meta).
Hoy el proceso es manual y telefónico: 25 a 40 min del reporte al despacho y reproceso en 1 de cada 5
despachos. El MVP es el capítulo 8 de un documento formal (Word) cuyos capítulos 6 y 7 describen el
diseño TO-BE y la arquitectura. **El código debe mantenerse coherente con ese documento**: si cambias
una regla de negocio, avisa al usuario para que actualice las secciones 6.6 y 8.

- Idioma: **todo en español** (UI, mensajes, comentarios, commits, docstrings).
- Todos los datos son **ficticios** (brigadistas, empresas, teléfonos, correos).
- Los umbrales de las reglas son **supuestos** del equipo, pendientes de validar con ARKOF.
- Fecha de entrega de este corte: **9 de octubre de 2026**.

## 2. Stack y arquitectura

```
Navegador (React) ──HTTP──> Flask API + motor de despacho ──SQLAlchemy──> SQLite
                                   │  ▲
                        webhook    │  │ POST /api/incidentes/<id>/verificar-sla (X-ARKOF-Token)
                                   ▼  │
                                  n8n ──> SMTP (Gmail) · Twilio (SMS)
```

- **Backend:** Python 3.10+, Flask 3, Flask-SQLAlchemy, Flask-Cors, requests, python-dotenv.
- **Frontend:** React 18 + Vite 5, CSS propio (sin frameworks de UI), fuentes Barlow y Source Sans 3
  vía `@fontsource`. Flask sirve `frontend/dist` en `http://localhost:5000`.
- **Automatización:** n8n 1.x. La app **no envía correos ni SMS directamente**: publica eventos JSON al
  webhook de n8n (`notificador.py`). Esta separación es una decisión de diseño documentada
  (capítulo 7.3): no metas envío de mensajes dentro de Flask.
- **Modo simulación:** si `N8N_WEBHOOK_URL` está vacía, los eventos no salen a n8n y un hilo vigilante
  (`VIGILANTE_SLA=1`) reemplaza al nodo Wait. En ambos modos la bandeja (`/api/notificaciones`) guarda
  cada evento con su canal y sus enlaces.
- **Autenticación por rol:** sesión en cookie firmada (`SECRET_KEY`), contraseñas con hash de Werkzeug.
  Roles `coordinador` (consola) y `brigadista` (portal). El control está en `control_de_acceso`
  (`app.py`): `/api/mi/*` es del brigadista, el resto de `/api/*` del coordinador; públicas `/api/salud`,
  `/api/auth/*`. `verificar-sla` acepta el secreto de n8n **o** una sesión de coordinador.
  El enlace del SMS (`/confirmar/<token>`) **no exige sesión** (decisión del documento, 6.4).

## 3. Estructura

| Ruta | Contenido |
|---|---|
| `backend/app.py` | Rutas de la API, autenticación y control de acceso, portal (`/api/mi/*`), previsualización (casilla 9), resumen de simulación, KPIs, vigilante de plazos, servir el front |
| `backend/templates/confirmar.html` | Página móvil del enlace del SMS (PRG: POST → 303 → GET con `?resultado=ok|ya`) |
| `backend/motor_despacho.py` | Lógica central: `registrar_y_despachar`, `clasificar`, `previsualizar`, `candidatos`, `seleccionar_brigada`, `kit_requerido`, `reservar_equipos`, `registrar_respuesta`, `deficit`, `_reemplazar`, `verificar_sla`, `avanzar_estado`, `cerrar`, `informe` |
| `backend/reglas.py` | Parámetros de RN-01 a RN-11 (umbrales, tamaños de brigada, certificaciones, kits, plazos, sobre-convocatoria, transiciones) |
| `backend/models.py` | Modelos: `EmpresaAfiliada`, `Brigadista`, `Equipo`, `Incidente`, `Asignacion` (`vence_en()`), `ReservaEquipo`, `Evento`, `Usuario` |
| `backend/notificador.py` | `payload()` y `enviar()` hacia n8n; bandeja `BANDEJA` con el canal de cada evento |
| `backend/semilla.py` | Datos de demo (4 bases, 14 brigadistas, 60 equipos, 3 empresas) y `crear_cuentas()`: `coordinador` + `nombre.apellido` por brigadista, clave `CLAVE_DEMO` |
| `backend/tests/` | 35 pruebas pytest: `test_despacho.py` (reglas) y `test_acceso.py` (roles, portal, enlace, bandeja, previsualización). `conftest.py` aísla del `.env` |
| `backend/simular_escenarios.py` | Simulación de eventos discretos AS-IS vs. TO-BE con el motor real y reloj simulado |
| `backend/demo_escenarios.py` | Carga 3 incidentes de demostración contra la app en ejecución (ingresa como coordinador) |
| `frontend/src/App.jsx` | Decide la vista por rol: `Ingreso`, `Consola` o `Portal` |
| `frontend/src/Consola.jsx` | Consola del coordinador: `Tablero`, `Reportar`, `Detalle`, `Recursos`, `Bandeja` (navegación por estado, sin router) |
| `frontend/src/Portal.jsx` | Portal móvil del brigadista |
| `frontend/src/comunes.jsx`, `api.js` | Componentes del formato (`Casilla`, `Sello`, `Nivel`, `CabezaHoja`, `Icono`), hooks y cliente HTTP |
| `frontend/src/styles.css` | Tokens y estilos del mundo visual (ver `DESIGN.md`) |
| `n8n/arkof_despacho_workflow.json` | Flujo de 13 nodos (id fijo `arkofDespacho001`): Webhook → Switch → (correo + SMS + Telegram de demostración por brigadista, Wait → HTTP verificar-sla) / aviso cliente / alerta coordinador (correo + SMS + Telegram) / informe de cierre |
| `n8n/iniciar_n8n.mjs` | Arranca, importa o activa n8n local con las variables de `backend/.env` |
| `n8n/enlazar_credenciales.py` | Genera `n8n/.flujo_enlazado.json` (no versionado) con los ids de las credenciales creadas en el editor |
| `PRODUCT.md`, `DESIGN.md` | Contexto de producto y sistema visual (skill de diseño Impeccable) |

## 4. Reglas de negocio (no cambiarlas sin avisar)

| Código | Regla |
|---|---|
| RN-01 | Nivel 2 si ≥ 5 bbl, sustancia peligrosa o cuerpo de agua/comunidad; nivel 3 si ≥ 50 bbl, agua + comunidad, o sustancia peligrosa + comunidad |
| RN-02 | Brigada: nivel 1 = 2 (1 líder), nivel 2 = 4 (1 líder), nivel 3 = 6 (2 líderes) |
| RN-03 | Elegible: disponible, certificación (derrame → ANTIDERRAME; sustancia/gas → HAZMAT), sin asignación activa en incidente no cerrado |
| RN-04 | Orden por distancia haversine y luego menor carga. Control de fatiga **sin exclusión**: quien suma 2 atenciones cerradas en las últimas 24 h (`atenciones_recientes()`) va al final; si no hay alternativa se le convoca, se registra `CONVOCATORIA_CON_FATIGA` y se alerta al coordinador |
| RN-05/06 | Kit por tipo y nivel, tomado de la base más cercana; 1 vehículo por cada 4 brigadistas |
| RN-07 | Plazo de confirmación: 5 min (niveles 1 y 2), 4 min (nivel 3); `SLA_DEMO_MIN` lo sobrescribe |
| RN-07b | Sobre-convocatoria: +0 / +1 / +2 técnicos; al completar la brigada, los sobrantes pasan a `no_requerido` |
| RN-08 | Reemplazo solo del **déficit** (confirmados + pendientes vs. requeridos); más de 2 rondas → coordinador |
| RN-09 | Recursos insuficientes → asignación parcial + alerta al coordinador |
| RN-10 | Cierre libera personal y equipos, suma atención 24 h e informe al cliente |
| RN-11 | Toda acción queda en `Evento`; transiciones según `TRANSICIONES` |

Estados de incidente: `reportado → notificado → confirmado → en_ruta → en_sitio → controlado → cerrado`.
Estados de asignación: `pendiente | confirmado | rechazado | vencido | no_requerido`.
Roles internos `lider` / `tecnico`; en la UI y los textos se muestran como "líder" / "técnico".
El front nunca duplica reglas: el plazo (`sla_minutos`, `vence_en`), el tamaño de brigada
(`brigada_requerida`) y la casilla 9 (`/api/incidentes/previsualizar`) vienen del backend.

**Bugs ya corregidos (no reintroducir):**
- Las asignaciones `confirmado` de incidentes cerrados no deben bloquear brigadistas (filtro `Incidente.estado != "cerrado"`).
- La reserva de equipos ordena por cercanía de la base.
- Un plazo corto en nivel 3 generaba reasignaciones en cadena; eso lo resuelve RN-07b.
- Las pruebas leían `backend/.env` (publicaban en n8n real y tardaban 2 s por evento): `conftest.py` fija las variables en vacío antes de importar la app.
- Con `N8N_SHARED_SECRET` configurado, "Forzar vencimiento" de la consola daba 401: ahora acepta sesión de coordinador.
- Telegram fallaba al azar ("can't parse entities") porque los tokens de los enlaces llevan `_` y el nodo usaba Markdown:
  los nodos de Telegram envían en HTML. Los nodos de SMS están **desactivados** (`disabled`) hasta tener plan pago de
  Twilio; Telegram va arriba en el lienzo para ejecutarse antes que el correo (orden de ejecución v1 de n8n) y la
  alerta de fatiga se publica después del despacho.
- El contador `atenciones_24h` nunca se reiniciaba y excluía para siempre a quien sumaba 2 atenciones: la carga se calcula
  por fecha de cierre en una ventana de 24 h y la fatiga ya no excluye. El simulador separa los incidentes más de 24 h
  para conservar su supuesto de personal descansado (cifras de la sección 6.8 verificadas idénticas).

## 5. Cómo ejecutar

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Frontend (compila a frontend/dist)
cd ../frontend && npm install && npm run build
# App (modo simulación si no hay N8N_WEBHOOK_URL)
cd ../backend && python app.py            # http://localhost:5000
# Desarrollo del front con recarga en caliente: npm run dev (puerto 5173, proxy a 5000)
```

Tras cambiar `semilla.py`, `CLAVE_DEMO` o las variables `DEMO_*`, borra `backend/instance/*.db` para
recrear la base. Una base anterior al login conserva sus datos: al arrancar se crean las cuentas que falten.

### Variables de entorno (`backend/.env`)

| Variable | Uso |
|---|---|
| `N8N_WEBHOOK_URL` | Production URL del webhook (local: `http://localhost:5678/webhook/arkof-despacho`) |
| `N8N_SHARED_SECRET` | Debe coincidir con el encabezado `X-ARKOF-Token` que envía n8n |
| `PUBLIC_BASE_URL` | Base de los enlaces del SMS y el correo (localhost, IP de la LAN o URL de ngrok) |
| `COORDINADOR_EMAIL`, `COORDINADOR_TELEFONO` | Destino de las alertas |
| `DEMO_EMAIL`, `DEMO_TELEFONO` | Redirigen todas las notificaciones a un correo y un celular reales |
| `VIGILANTE_SLA` | `1` = temporizador interno; `0` cuando n8n está activo |
| `SLA_DEMO_MIN` | Plazo corto para demos (p. ej. `1`) |
| `SECRET_KEY` | Firma de la cookie de sesión |
| `CLAVE_DEMO` | Contraseña de las cuentas de demostración |
| `TWILIO_FROM_NUMBER`, `ARKOF_CORREO_REMITENTE` | Las lee n8n (vía `n8n/iniciar_n8n.mjs`): número de Twilio y *From* de los correos |
| `DEMO_TELEGRAM_CHAT_ID` | Canal de **demostración**: el payload lleva `telegram_chat_id` y `coordinador_telegram`, y n8n envía también por Telegram. El SMS sigue siendo el canal de producción (la cuenta gratuita de Twilio no envía a Colombia) |

### n8n local

```bash
node n8n/iniciar_n8n.mjs importar   # importa/actualiza el flujo
node n8n/iniciar_n8n.mjs activar    # lo activa
node n8n/iniciar_n8n.mjs            # http://localhost:5678 (datos en ~/.arkof-n8n, fuera del repo)
```

El script toma `N8N_SHARED_SECRET`, `TWILIO_FROM_NUMBER` y `ARKOF_CORREO_REMITENTE` de `backend/.env` y fija
`N8N_BLOCK_ENV_ACCESS_IN_NODE=false`. Las credenciales SMTP (Gmail con contraseña de aplicación,
`smtp.gmail.com:465` SSL) y Twilio (Account SID + Auth Token) se crean **dentro del editor de n8n**, no en
el código. En n8n Cloud no hay variables de entorno propias: el secreto, el número *From* y el remitente
se escriben directo en los nodos.

## 6. Pruebas y verificación

```bash
cd backend
python -m pytest -q                 # deben pasar las 35 (~20 s)
python demo_escenarios.py           # con la app corriendo
python simular_escenarios.py 300    # semilla 2026; resultados en resultados_simulacion.json
```

Resultados de referencia (citados en el documento, sección 6.8): AS-IS 30,1 min de media frente a
TO-BE 6,4 min (−78,7 %), p90 de 40,4 a 11,1 min, 91,3 % sin intervención manual y 8,7 % escalado al
coordinador. **Si un cambio altera estos números, avisa al usuario**, porque están en el documento.

Toda regla nueva o modificada debe tener su prueba. Antes de dar una tarea por terminada:
pytest en verde + `npm run build` sin errores.

## 7. Convenciones

- Sistema visual: "formulario de campo HSE autocopiante" (original blanco = coordinación, copia amarilla =
  brigadista). Detalle en `DESIGN.md`; el contrato de dirección está como comentario en `frontend/index.html`.
- Paleta (compartida con los diagramas del documento): navy `#1F3B4D`, verde `#5B7A63`, verde claro
  `#8FAE9A`, menta `#E4EFE8`, arena `#F4D9B0`, café `#5B4636`, alerta `#8A5A2B`.
- UI en español, voz activa, sin mayúsculas sostenidas en etiquetas; los botones dicen lo que hacen.
- Mantener el MVP simple: sin nuevas dependencias pesadas, sin ORM alternativo, sin router en el front
  salvo que se pida.
- Los parámetros de negocio van en `reglas.py`, nunca dentro del motor.
- **Credenciales:** nunca escribir Account SID, Auth Token, contraseñas de aplicación ni secretos reales
  en el código, en `.env.example` ni en commits. `.env` está en `.gitignore`.
- Mantener compatibles los nombres de campos del payload de `notificador.payload()`: el flujo de n8n
  los usa (`body.evento`, `body.destinatarios[].url_confirmar`, `url_rechazar`, `url_portal`, `usuario`,
  `telegram_chat_id`, `body.coordinador_telegram`, `body.sla_minutos`, `body.url_verificar_sla`, `body.incidente.*`, `body.informe.*`, `body.motivo`).
  Si cambian, actualizar el JSON de n8n.

## 8. Pendientes y mejoras sugeridas

Hechos: botón "Ver como brigadista"; enlaces visibles también con n8n activo; estado final claro en
`/confirmar`; autenticación por rol (coordinador y brigadista).

1. Rol de gerencia de solo lectura (tablero de KPIs), mencionado en el documento (6.5 y 7.6).
2. Endurecer la autenticación: cambio y recuperación de contraseña, bloqueo por intentos, HTTPS.
3. Opcional: Dockerfile y `docker-compose` (app + n8n) para simplificar la reproducción.

## 9. Limitaciones conocidas (declaradas en el documento)

Distancias en línea recta (no rutas viales), autenticación básica (sin gerencia ni recuperación de
clave), SQLite y ejecución local, datos y comportamiento humano simulados. La arquitectura objetivo
(AWS, PostgreSQL, contenedores) está en el capítulo 7 y **no** se implementa en el MVP.
