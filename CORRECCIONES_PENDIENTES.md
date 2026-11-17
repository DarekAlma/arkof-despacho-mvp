# Correcciones pendientes — entrega final ARKOF (capítulos 9 a 13)

Estado al 16 de noviembre de 2026. Sale de la auditoría de los capítulos 9 a 13.
Este archivo es de trabajo: no hace parte de la entrega.

## Estado: ya aplicado en esta sesión

Las casillas de abajo quedaron sin marcar, pero **B1 a B7, M1 a M11 y Docker ya están aplicados** en:

- `C:\Users\rogst\Downloads\ARKOF_Entrega_Final_Cap1-13_v2.docx` y `_v2.pdf` (81 páginas; el original no se tocó).
- Repositorio (sin commit): `docker-compose.yml` nuevo y probado, `README.md`, `backend/motor_despacho.py`,
  `docs/manual_usuario.pdf`, y `CLAUDE.md`, `DESIGN.md`, `PRODUCT.md` retirados del índice de git.

**Falta:**

1. Revisar el `_v2.docx` completo en Word antes de entregar (solo se revisó una página a la vista y el texto del PDF).
2. Hacer commit y push del repositorio (no se hizo: requiere su aprobación).
3. Actualizar `CLAUDE.md`: mencionar `docker-compose.yml` y el pendiente 3 de la sección 8, ya hecho para n8n.
4. Todo lo de la sección «Solo el equipo puede resolver».
5. La cita [31] (Ley 2101 de 2021) se agregó sin enlace: confirmar el título y agregar la URL oficial.
6. Valores reales de M2: VPN $ 2.866.094 (−30 %) y $ 18.049.411 (+30 %).

## Cómo se regenera el documento

- Documento entregado: `C:\Users\rogst\Downloads\ARKOF_Entrega_Final_Cap1-13.docx` (+ PDF). No sobrescribirlo:
  guardar la versión corregida como `ARKOF_Entrega_Final_Cap1-13_v2.docx`.
- Generador (Python, reproduce el documento exacto salvo el índice):
  `C:\Users\rogst\AppData\Local\Temp\claude\05e5a6539abbd1d2\195a6c0f-0e12-47d4-af9f-d18cbb8a3407\scratchpad\final\`
  - `build.py` parte de `Downloads\ARKOF_Entrega2_Cap1-8_FINAL.docx` e inserta los capítulos nuevos.
  - `cap9_11.py` y `cap12_13.py` tienen el texto de los capítulos 9 a 13 y las conclusiones.
  - `finanzas.py` es el modelo financiero; `riesgos.py`, la matriz; `anotar.py`, las capturas con letras.
  - Copia de trabajo de esta sesión:
    `C:\Users\rogst\AppData\Local\Temp\claude\260087191b521f61\675d5b98-805d-4a2b-b11e-d36c3e255188\scratchpad\gen\`
- Después de `python build.py`: abrir en Word, actualizar el índice (clic derecho → Actualizar campos → toda la tabla)
  y exportar a PDF.
- Las carpetas temporales pueden borrarse al reiniciar el equipo. Si no existen, las correcciones se hacen a mano en Word
  con los textos de abajo.

## Regla: no cambiar cifras

Todas las cifras del capítulo 9 están verificadas y coinciden. Ninguna corrección de esta lista cambia CAPEX, OPEX,
VPN, TIR, ROI ni recuperación. Si alguna las cambia, hay que actualizar también 1.8, 12.1, 12.2, 12.4 y Conclusiones.

## Bloqueantes

- [ ] **B1. Piloto: 4 semanas (9.2) frente a tres meses (9.6, 12.1, Recomendaciones).**
  Dejar tres meses en todo el documento sin tocar el valor.
  - 9.2, tabla CAPEX: «Pruebas de calidad y piloto de 4 semanas (60 h)» → «Pruebas de calidad y acompañamiento del
    piloto de tres meses (60 h)».
  - 9.6: «un piloto de tres meses en una base, que cuesta una fracción del CAPEX, mide…antes de la inversión completa»
    → «un piloto de tres meses en una base, cuyo acompañamiento técnico ya está presupuestado en el CAPEX (60 horas,
    $ 2.700.000), mide el volumen real y los tiempos de coordinación y permite recalcular este modelo con datos de
    ARKOF antes de extender la operación a las demás bases».
  - Recomendaciones y 12.4: «antes de la inversión completa» → «antes de extenderla a las demás bases».

- [ ] **B2. Soporte 24/7 prometido en 10.7 y no costeado en 9.2.**
  - Agregar después de la tabla de 10.7: «El “administrador de TI” de estas tablas no es un cargo nuevo: es el
    proveedor de soporte contratado con las 8 horas mensuales del OPEX (capítulo 9.2), en horario hábil. Por eso
    ningún plan depende de él para atender la emergencia: el coordinador activa la contingencia de inmediato y el
    soporte restablece el servicio después. Una disponibilidad 24/7 con tiempos garantizados exige un contrato de
    soporte adicional, que no está en el modelo y debe cotizarse si el piloto lo justifica.»
  - Tiempos objetivo de 10.7: plataforma caída → «Activación inmediata; restablecimiento en el siguiente día hábil»;
    n8n caído → «Inmediato desde la vista Notificaciones; restablecimiento en el siguiente día hábil»; proveedor de
    SMS → «Siguiente día hábil (correo y mensajería siguen activos)»; pérdida de datos → «Siguiente día hábil»;
    acceso no autorizado → «El mismo día hábil».

- [ ] **B3. El 13.2 no basta para instalar n8n.** Reescribir «Instalación y configuración»:
  - Decir dónde está la contraseña de demostración: `CLAVE_DEMO` en `backend/.env` o, si no se define,
    `CLAVE_DEMO_POR_DEFECTO` en `backend/semilla.py`.
  - El paso de n8n se ejecuta desde la raíz del repositorio: agregar `cd ..` (el paso 1 deja la terminal en `backend/`).
  - «Node.js 18 o superior» → «Node.js 20 o superior» (dos veces: tabla de dependencias y requisitos previos).
  - n8n en Docker (así se ejecutó el MVP, según el equipo): documentar el `docker-compose.yml` del repositorio
    (ver sección «Docker» abajo) y dejar `node n8n/iniciar_n8n.mjs` como alternativa sin Docker.
  - Agregar los pasos que faltan: crear la cuenta de n8n en `http://localhost:5678/setup`; credencial SMTP de Gmail
    (`smtp.gmail.com`, puerto 465, SSL, contraseña de aplicación); bot de Telegram con @BotFather y
    `DEMO_TELEGRAM_CHAT_ID`; `VIGILANTE_SLA=0` cuando n8n controla el plazo; detener n8n antes de
    `python n8n/enlazar_credenciales.py`, reimportar y volver a activar.
  - Tabla de variables: agregar `DATABASE_URL` (por defecto SQLite; en producción, PostgreSQL).
  - Tabla de API: agregar `GET /api/empresas` y `POST /api/demo/reiniciar` (solo demostración: borra los datos).

- [ ] **B4. Evidencia de trabajo en equipo (12.5).** Quitar «el repositorio conserva el historial de cambios del
  código»: GitHub muestra 3 commits del 9 de octubre, de una sola cuenta. Poner en su lugar una tabla de integrante,
  rol (capítulo 1.9) y bloque del pitch, más las tres entregas con fecha (21 de agosto, 9 de octubre, 25 de noviembre).
  **Lo debe completar el equipo:** aportes reales por integrante y actas o fechas de reunión, si existen.

- [ ] **B5. Repositorio desactualizado en GitHub.**
  - `git pull --rebase --autostash` (GitHub tiene un commit con el enlace del video en el README).
  - Subir los cambios locales: `README.md`, `.gitignore`, `docs/capturas/08_n8n_flujo.png`.
  - README: cambiar «entregable del capítulo 8» por «capítulos 8 y 13», enlazar el manual y el video, «Node.js 20+».
  - `CLAUDE.md`, `DESIGN.md` y `PRODUCT.md` siguen publicados aunque estén en `.gitignore`:
    `git rm --cached CLAUDE.md DESIGN.md PRODUCT.md` y luego commit.

- [ ] **B6. Figura 26 (13.3, Tarea 2).** La letra E dice «Botones para avanzar el estado y cerrar» pero la captura solo
  muestra «Forzar vencimiento del plazo (demo)». Texto nuevo:
  - C: agregar «Los botones “Confirma” y “Rechaza” sirven para registrar la respuesta de quien avisó por teléfono.»
  - E: «Acciones del coordinador. Mientras la brigada responde solo aparece “Forzar vencimiento del plazo (demo)”,
    que existe únicamente en la versión de demostración. Cuando la brigada se completa, aquí aparecen los botones
    para avanzar el estado y cerrar (Tarea 3).»

- [ ] **B7. Residuos de versiones anteriores.**
  - Referencias, última página: eliminar la nota que termina en «deberá incorporarse… en la próxima entrega».
  - 1.1: el título dice «ARKOF S.A.S AUTOMATIZACIÓN v1.0» → «v3.0».
  - 12.3, paso 7: «(Figura 15)» → «(Figuras 15 y 16)».

## Mejoras

- [ ] **M1. Volumen sin respaldo (9.1).** Agregar a la justificación del volumen: «Supuesto sin dato de ARKOF. El
  equilibrio de 11,8 incidentes al mes (sección 9.5) es el umbral que la gerencia debe contrastar con su operación.»
- [ ] **M2. «Deliberadamente conservadores» (9.1).** Cambiar por «prudentes en lo que monetizan». Agregar a la tabla de
  sensibilidad (9.5) la fila «Tasa de despachos fallidos en el AS-IS»: con −30 % (14 %, el valor de la corrida
  simulada del 6.8) el VPN es $ 2.866.101; con +30 % (26 %), $ 18.049.404. La frase «el volumen es la única variable
  que vuelve negativo el VPN» sigue siendo cierta.
- [ ] **M3. Divisor de 192 horas (9.1).** Agregar: «192 horas equivalen a 48 horas semanales por 4 semanas. La jornada
  legal vigente es menor (Ley 2101 de 2021), de modo que el costo real por hora, y con él el ahorro, sería mayor.»
  Verificar la cita de la ley antes de entregar.
- [ ] **M4. Ahorro que no es caja (9.4).** Agregar: «Los dos beneficios de tiempo ($ 7.950.000, el 56 % del total) son
  horas liberadas de personal asalariado: se convierten en dinero solo si ARKOF las dedica a servicios facturables o
  evita contratar.»
- [ ] **M5. Posible doble conteo (9.4).** Aclarar: «El informe lo elabora hoy un auxiliar administrativo después de la
  atención; no hace parte de las horas del coordinador de la primera fila.»
- [ ] **M6. Precios (9.2).** Marcar como supuesto: «USD 0,0525 por segmento es un supuesto del equipo: la tarifa oficial
  [24] no pudo confirmarse y las fuentes consultadas la ubican entre USD 0,02 y 0,05. Con USD 0,20 el VPN sigue
  positivo ($ 5.863.826).» Lightsail y n8n: «valores de referencia por confirmar al contratar».
- [ ] **M7. T3: el SMS llega sin datos, pero confirmar por el enlace sí los necesita.** Corregir 10.3 (T3), 11.1
  (mensajería) y 12.4. Proponer la respuesta por SMS de texto como mejora posterior al piloto, fuera del CAPEX.
- [ ] **M8. Afirmaciones sin respaldo.**
  - T2 y 10.7: «proveedor de SMS alterno identificado» → «proveedor alterno por seleccionar antes de producción».
  - T4 y 11.1: «tokens de un solo uso» → «token único por convocatoria, que deja de admitir respuesta tras la
    primera». Añadir que el rechazo desde el correo hoy se registra con solo abrir el enlace y que en producción
    debe pedir confirmación en la página.
  - `backend/motor_despacho.py:196`: la bitácora dice «por correo + SMS» con el SMS desactivado.
- [ ] **M9. Manual aparte.** Exportar el 13.3 a `docs/manual_usuario.pdf` y citarlo en la tabla del 13.4. Si existen
  diapositivas, agregarlas a esa tabla.
- [ ] **M10. Jerga del manual (13.3).** «n8n» → «el servicio de avisos»; agregar al glosario HSE, HAZMAT y EPP; quitar
  la remisión al «capítulo 10.7» de la tabla de errores; «Abrir enlace para copiarlo» → «abre la página en otra
  pestaña; copie su dirección»; en la letra C del tablero, decir que el recuadro cambia a «Requieren su decisión».
- [ ] **M11. Otros.**
  - 9.3: explicar la base de B ($ 6.000.000 de configuración inicial; 16 usuarios = 14 brigadistas, coordinador y
    gerencia) y de C (canal dedicado $ 2.400.000 al año; energía y repuestos $ 1.200.000 al año).
  - 9.2: desglosar «Capacitación y gestión del cambio $ 1.174.000»: 12 h de facilitación ($ 540.000), 4 h de
    coordinadores ($ 144.000) y 2 h por cada uno de 14 brigadistas ($ 490.000).
  - 10.6: agregar la calificación residual de T3, O1 y O3 (hoy solo dice que «bajan a alto o medio»).
  - Conclusiones y 12.1: «los riesgos críticos son operativos, no tecnológicos» → «dependen de la operación y del
    entorno, no del software» (T3 está en la tabla de riesgos técnicos).
  - Referencias [3], [9] y [10] no se citan en el texto.

## Docker

El equipo indica que n8n se ejecutó en contenedores de Docker. En este equipo no hay contenedor ni imagen de n8n, y
el repositorio lo arranca con `npx` (`n8n/iniciar_n8n.mjs`, versión 1.123.83). Para que el documento y el repositorio
coincidan:

- [ ] Agregar `docker-compose.yml` en la raíz con el servicio `n8n` (imagen `n8nio/n8n` 1.123.x, puerto 5678, mismas
  variables que `iniciar_n8n.mjs`, datos en `~/.arkof-n8n/.n8n` para que `enlazar_credenciales.py` siga funcionando).
- [ ] Con n8n en un contenedor, `PUBLIC_BASE_URL` debe ser alcanzable desde el contenedor: la URL de ngrok o
  `http://host.docker.internal:5000`. `http://localhost:5000` no sirve: n8n no podría llamar a `verificar-sla`.
- [ ] Actualizar 9.2 («n8n se ejecutó… local, en un contenedor de Docker»), 11.1 (fila Nube) y 13.2.
- [ ] El capítulo 8.4 describe la ruta con `node`; agregar allí una frase que remita al 13.2.

## Solo el equipo puede resolver

- Volumen real de incidentes, validado con ARKOF.
- Aportes por integrante y evidencia de reuniones (B4).
- Confirmar el reparto de presentadores del pitch (12.1 dice que es una propuesta).
- Capturas nuevas para las tareas 3, 4 y 5 del manual («Brigadistas y equipos», «Notificaciones», informe de cierre).
- Revisar que el video dure entre 5 y 10 minutos y tenga narración (no se verificó su contenido).
