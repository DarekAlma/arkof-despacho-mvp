# Encargo de auditoría — Capítulos 9 a 13 del proyecto ARKOF

Eres un auditor académico exigente y un revisor técnico. Tu trabajo es verificar si los capítulos 9 a 13 y la
sección de conclusiones del informe final cumplen la guía del curso y si son coherentes con el resto del documento y con
el código. **No reescribas el documento.** Entrega hallazgos verificables. Cada hallazgo indica la sección, la evidencia y
la corrección propuesta.

## 1. Contexto

- **Curso:** Gerencia de Operaciones de TI (IT Operations Management), Universidad de La Sabana, 2026-2.
- **Docente:** Mateo Barón Rojas.
- **Equipo:** Darek Aljuri Martínez, Valentina Ruiz Torres y Santiago Soler Prado.
- **Proyecto:** automatización del despacho de brigadas ante contingencias ambientales para ARKOF S.A.S.
  (Villavicencio, Meta). Hoy el proceso es manual y telefónico.
- **MVP:**
  - backend en Flask y SQLite;
  - frontend en React y Vite;
  - automatización en n8n (correo y Telegram activos; SMS por Twilio desactivado porque la cuenta gratuita no envía a
    Colombia).
- **Repositorio:** https://github.com/DarekAlma/arkof-despacho-mvp
- **Video:** https://www.youtube.com/watch?v=wSBJssc8Row
- **Datos y supuestos:** todos los datos son ficticios. ARKOF no compartió volumen, nómina ni costos, así que las cifras
  financieras son supuestos del equipo.

## 2. Archivos que debes recibir

1. `ARKOF_Entrega_Final_Cap1-13.docx` o su PDF (80 páginas). Es el documento auditado.
2. La guía del curso (`Course_Project_Guidelines_GOTI.docx`) o, si no la tienes, el extracto de la sección 3.
3. Opcional: el repositorio, o al menos `README.md`, `backend/reglas.py`, `backend/app.py`, `backend/models.py` y
   `n8n/arkof_despacho_workflow.json`.

Si te falta un archivo, dilo y audita con lo que tengas. No supongas su contenido.

## 3. Requisitos de la guía (capítulos 9 a 13)

**9. Cost and Investment Model**
- Detailed cost estimation: Development, Infrastructure, Licenses, Maintenance.
- CAPEX vs. OPEX analysis.
- Financial benefits from automation: Cost savings, Productivity gains, Operational efficiency.
- Return on Investment (ROI).
- Estimated payback period.
- Students must justify their financial assumptions and demonstrate the economic feasibility of the project.

**10. Risk Management**
- Risk matrix (impact vs. probability).
- Technical risks.
- Operational risks.
- Change management and adoption risks.
- Mitigation strategies.
- Contingency plans.
- Students must identify potential implementation challenges and propose realistic solutions.

**11. Innovation & Emerging Technologies**
- Technologies used (Cloud, RPA, AI/ML, IoT, Big Data, etc.).
- Justification for selecting these technologies.
- Contribution to Innovation, Competitive advantage, Operational excellence and Scalability.
- Students must explain how technology generates value and addresses the identified problem.

**12. Final Presentation (15 minutes)**
- Covers: problem or opportunity; proposed solution; operational and business impact; financial feasibility and key
  risks; technological architecture.
- Visual support: process diagrams, AS-IS vs. TO-BE comparison, architecture diagrams.
- Live or recorded demonstration of the MVP (chapter 8).
- Evidence of teamwork and feasibility.
- Pitched as if to decision-makers or clients.

**13. Complete Documentation and Final Submission**
- **13.1 Final Report.** All chapters, process and architecture diagrams, AS-IS vs. TO-BE, tables and risk matrices,
  budget and financial analysis, MVP results, conclusions and recommendations.
- **13.2 Technical Documentation.**
  - Source code or workflows; system architecture and components.
  - Languages, frameworks and dependencies; database structure.
  - Installation and configuration; required integrations and APIs.
  - Running and testing; technical limitations and maintenance recommendations.
  - Expected outcome: *a developer who did not participate can understand, install, configure and execute the solution.*
- **13.3 User Manual.**
  - Purpose of the solution and target users; requirements.
  - Step-by-step access; main functionalities.
  - Screenshots and practical examples; common tasks.
  - Frequent errors and solutions.
  - Clear language with no unnecessary jargon.
  - Expected outcome: *a non-technical user can operate it independently.*
- **13.4 MVP and Demonstration Package.** Functional MVP, source code or workflows, technical documentation, user
  manual and demo video, all organized and clearly identified.

**El docente insistió en este criterio:** el proyecto debe demostrar tres competencias. La **técnica** es una solución
funcional. La de **negocio** es viabilidad financiera, riesgos e impacto operativo. La de **comunicación** es
traducir lo técnico a conocimiento práctico. La calidad de la documentación técnica y funcional es esencial en la nota.

## 4. Qué debes revisar

### 4.1 Cumplimiento de la guía
Para cada viñeta de la sección 3, marca **Cumple**, **Parcial** o **No cumple**. Cita la sección y la página donde
está la evidencia. Un "Parcial" debe decir exactamente qué falta.

### 4.2 Recalcular las cifras del capítulo 9
Rehaz los cálculos a mano o en código con los supuestos de la tabla 9.1 y compáralos con estos valores esperados. Un
redondeo de hasta 1 % es aceptable.

| Concepto | Fórmula | Valor esperado |
|---|---|---|
| Brigada promedio | 0,5×2 + 0,35×4 + 0,15×6 | 3,3 personas |
| Costo de un despacho fallido | 1,5 h × 3,3 × $17.500 + 60 km × $1.800 | ≈ $195.000 |
| CAPEX | 240 h, 60 h y 30 h a $45.000; 20 h a $14.500; capacitación $1.174.000; contingencia 10 % | $17.945.000 |
| OPEX anual (base) | nube USD 30/mes; SMS 180×12×USD 0,0525 + USD 1,15/mes; dominio $120.000; mantenimiento 8 h/mes × $45.000; TRM 4.000 | $6.388.800 |
| Beneficio anual (base) | coordinación 180×(1,25−17,5/60)×$36.000; errores 180×0,18×$195.000; informe 180×(40/60)×$14.500 | $14.268.000 |
| Flujo neto anual | beneficio − OPEX | $7.879.200 |
| VPN a 5 años, 12 % | −CAPEX + Σ neto/(1,12)^t | ≈ $10.457.753 |
| TIR | — | ≈ 33,6 % |
| ROI a 5 años | (5·beneficio − (CAPEX + 5·OPEX)) / (CAPEX + 5·OPEX) | ≈ 43,0 % |
| Recuperación simple | CAPEX / neto | ≈ 2,28 años (27 meses) |
| Equilibrio (VPN = 0) | volumen mensual que anula el VPN | ≈ 11,8 incidentes/mes |
| Escenarios | 8 / 15 / 25 incidentes al mes | VPN ≈ −12,8 / +10,5 / +43,7 millones |

Verifica también:
- que el CAPEX y el OPEX mensual caigan en los rangos del capítulo 1.8 ($8 a $20 millones y $300.000 a $800.000);
- que la tabla CAPEX vs. OPEX (9.3) sume bien;
- que el análisis de sensibilidad sea consistente: solo el volumen vuelve negativo el VPN.

### 4.3 Calidad de los supuestos financieros
Evalúa si cada supuesto está justificado y si es razonable para una pyme colombiana en 2026: salarios, factor
prestacional de 1,52, tarifa de desarrollo, costo del despacho fallido, tasa de descuento del 12 %, precio del SMS y
TRM. Señala los que te parezcan débiles o inflados. El precio del SMS de Twilio para Colombia **no se confirmó en la
fuente oficial**: había cifras de USD 0,02 a 0,05 en sitios de terceros. Evalúa si eso cambia la conclusión.

### 4.4 Coherencia interna con los capítulos 1 a 8
Comprueba que no haya contradicciones con estas cifras y afirmaciones de capítulos anteriores:
- **Simulación (6.8):** AS-IS 30,1 min frente a TO-BE 6,4 min (−78,7 %); p90 de 40,4 a 11,1 min; 91,3 % sin
  intervención y 8,7 % escalado.
- **Escalamientos (6.8):** el 20,0 % de los incidentes con sustancias y el 19,6 % de los de nivel 3.
- **Línea base (2.4):** 25 a 40 min; 1 de cada 5 despachos con error; 1 a 1,5 h de coordinación por incidente.
- **Reglas:** plazos de RN-07 de 5/5/4 minutos; tamaños de brigada 2/4/6; sobre-convocatoria +0/+1/+2.
- **Fatiga (RN-04):** prioriza sin excluir y usa una ventana de 24 h.
- **Pendientes:** el capítulo 7.2 dejó pendiente "evaluar WhatsApp en el capítulo 11". Verifica que el 11.2 lo resuelva.
- **SMS:** el capítulo 5.2 y el 8 dicen que el costo del SMS se cuantifica en el capítulo 9. Verifica que así sea.
- **Hitos y versión:** el capítulo 1.7 fija el hito 5 el 25 de noviembre de 2026; revisa que la versión y la fecha del
  1.1 coincidan.
- **Numeración:** figuras 20 a 27 y referencias [24] a [30], sin saltos ni duplicados, y cada referencia citada en el
  texto.

### 4.5 Exactitud técnica frente al código (si tienes el repositorio)
Contrasta el capítulo 13.2 con el código. Revisa al menos:
- rutas de la API y control de acceso por rol (`app.py`);
- tablas y campos (`models.py`);
- nombres de los eventos de n8n: `despacho`, `escalamiento`, `confirmado`, `alerta_coordinador` y `cierre`;
- variables de entorno (`.env.example`);
- comandos de instalación y pruebas (deben dar 35 pruebas que pasan);
- etiquetas de botones citadas en el manual: «Registrar y despachar», «Confirmo, voy en camino», «No estoy disponible»,
  «Marcar “En ruta”», «Cerrar y enviar informe al cliente», «Ver como brigadista», «Abrir enlace».

### 4.6 Prueba del lector objetivo
- **Desarrollador externo:** siguiendo solo el 13.2 y el README, ¿podría instalar, configurar n8n, ejecutar y probar?
  Lista cada paso donde se quedaría bloqueado o tendría que adivinar.
- **Usuario no técnico:** lee el 13.3 como coordinador y como brigadista sin experiencia. ¿Hay jerga sin explicar?
  ¿Algún paso supone conocimiento previo? ¿Las capturas con letras A, B, C coinciden con el texto?

### 4.7 Calidad del pitch (capítulo 12)
- ¿Cabe en 15 minutos?
- ¿Cubre todos los puntos de la guía?
- ¿Usa los apoyos visuales exigidos?
- ¿Es convincente para una gerencia?
- ¿La evidencia de trabajo en equipo (12.5) es suficiente o es débil?

### 4.8 Redacción y forma
- Español correcto, voz activa y tono formal.
- Ninguna afirmación sin respaldo.
- Supuestos marcados como tales.
- Tablas legibles y figuras con pie.
- Nada de texto que suene a relleno.

## 5. Debilidades que el autor ya conoce (confírmalas o descártalas)

1. Todas las cifras financieras son supuestos; el volumen de incidentes no está validado con ARKOF.
2. Las capturas del manual (13.3) son las mismas del capítulo 8, ahora anotadas; no hay capturas nuevas de «Brigadistas
   y equipos», «Notificaciones» ni del informe de cierre.
3. El manual y la documentación técnica están dentro del informe y no como archivos aparte en el repositorio.
   Valora si el 13.4 exige entregarlos por separado.
4. El reparto de presentadores del pitch es una propuesta y no lo ha confirmado el equipo.
5. Al final de Referencias quedó una nota de una entrega anterior que dice "deberá incorporarse ... en la próxima
   entrega", y esta ya es la entrega final.
6. Los precios de Lightsail y n8n salieron de fuentes secundarias.

## 6. Formato de tu respuesta

1. **Veredicto general** (3 a 5 líneas): ¿está lista para entregar? Califica cada competencia de 1 a 5: técnica,
   negocio y comunicación.
2. **Matriz de cumplimiento:** una tabla con requisito, estado (Cumple, Parcial o No cumple), evidencia (sección y
   página) y comentario.
3. **Verificación de cifras:** una tabla con concepto, valor esperado, valor en el documento y ¿coincide?
4. **Hallazgos priorizados.** Separa los **bloqueantes** (afectan la nota o son errores) de las **mejoras**. Cada
   hallazgo indica la sección, el problema, la evidencia y la corrección concreta, con el texto sugerido si aplica.
5. **Lo que está bien:** máximo 5 puntos, solo si son relevantes.

Sé específico. "Mejorar la redacción" no es un hallazgo; "en 9.4, la frase X dice Y pero la tabla dice Z" sí lo es.
