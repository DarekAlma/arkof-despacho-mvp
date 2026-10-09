# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Coordinador de operaciones / HSE de ARKOF (administrador):** opera la consola en escritorio. Registra incidentes (propios o recibidos por teléfono), supervisa la brigada propuesta, atiende excepciones (rechazos, plazos vencidos, recursos insuficientes), avanza los estados de campo y cierra con informe.
- **Brigadista (líder o técnico):** recibe correo y SMS con un enlace de un solo uso y, desde su celular en campo (zonas rurales de Meta y Casanare, conectividad limitada, luz solar), confirma o rechaza con un toque. Además tiene cuenta propia para ver y contestar todas sus asignaciones.
- **Audiencia de evaluación:** el docente del curso y el video de demostración (5 a 10 min). La interfaz debe leerse con claridad en una grabación y una presentación.

## Product Purpose

MVP académico (Gerencia de Operaciones de TI, Universidad de La Sabana, 2026-2) que automatiza la gestión y el despacho de brigadas de ARKOF S.A.S. ante contingencias ambientales (derrames de hidrocarburos, sustancias nocivas, fugas de gas). Reemplaza un proceso manual y telefónico de 25 a 40 min por un flujo en el que el sistema clasifica, selecciona la brigada, reserva el kit y notifica en paralelo en milisegundos. Éxito: brigada confirmada en ≈6 min (simulado), 0 % de despachos con recurso no disponible y 100 % de trazabilidad.

## Positioning

El valor viene de paralelizar, no de acelerar: el coordinador sale del camino crítico y solo atiende excepciones. Todo queda en una bitácora inmutable que se convierte en el informe de cierre para el cliente y la autoridad ambiental.

## Operating Context

- Ciclo del incidente: reportado → notificado → confirmado → en ruta → en sitio → controlado → cerrado.
- Asignaciones: pendiente, confirmado, rechazado, vencido, no requerido; con cuenta regresiva del plazo (5 min niveles 1-2, 4 min nivel 3).
- Niveles de severidad 1, 2, 3 (RN-01). Reglas RN-01 a RN-11 en `backend/reglas.py`.
- n8n envía correo (SMTP) y SMS (Twilio); si no está configurado, la app funciona en modo simulación con una bandeja de eventos.
- Documento formal (Word, capítulos 1 a 8) con diagramas BPMN y figuras que usan la misma paleta; las capturas de la app se usan como figuras 12 a 14.

## Capabilities and Constraints

- Stack: Flask + SQLite + React 18/Vite, CSS propio, sin frameworks de UI ni router; sin dependencias pesadas nuevas.
- Todo en español; voz activa; sin mayúsculas sostenidas en etiquetas; los botones dicen lo que hacen.
- Dos roles: coordinador (administrador) y brigadista. Gerencia de solo lectura queda fuera por decisión del usuario.
- El enlace de confirmación por SMS funciona sin iniciar sesión (conectividad rural, sección 6.4 del documento).
- Datos ficticios; umbrales son supuestos pendientes de validar con ARKOF.

## Brand Commitments

- Paleta compartida con los diagramas del documento: navy `#1F3B4D`, verde `#5B7A63`, verde claro `#8FAE9A`, menta `#E4EFE8`, arena `#F4D9B0`, café `#5B4636`, alerta `#8A5A2B`. En los diagramas, verde = tarea del sistema y arena = tarea de personas.
- Tipografía: Barlow (títulos, cifras) y Source Sans 3 (texto), vía `@fontsource`.
- No debe parecer una plantilla SaaS genérica: es una herramienta de operación de emergencias ambientales.

## Evidence on Hand

- Resultados de simulación reales del MVP: AS-IS 30,1 min vs. TO-BE 6,4 min (−78,7 %), p90 40,4 → 11,1 min, 91,3 % sin intervención manual (`backend/resultados_simulacion.json`).
- Línea base AS-IS del capítulo 2: 25 a 40 min, 10 a 15 min de verificación, 1 de cada 5 despachos con reproceso.
- No hay logotipo oficial de ARKOF en el repositorio; no inventarlo.

## Product Principles

1. El coordinador supervisa excepciones, no ejecuta tareas: lo que requiere su atención debe saltar a la vista.
2. Cada pantalla demuestra la mejora frente al AS-IS con datos, no con adjetivos.
3. El brigadista responde en un toque, en campo y con sol, sin leer de más.
4. La trazabilidad es visible: cada acción tiene hora, actor y regla.
5. Coherencia con el documento: mismos nombres, reglas, estados y colores.

## Accessibility & Inclusion

- Portal del brigadista: contraste alto y objetivos táctiles grandes para uso a pleno sol y con guantes; funciona en cualquier navegador móvil sin instalar nada.
- Estados nunca comunicados solo por color (siempre con texto).
