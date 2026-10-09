---
name: ARKOF Despacho
description: Formato de campo HSE autocopiante que el sistema llena solo, casilla por casilla, para despachar brigadas ante contingencias ambientales.
colors:
  navy: "#1f3b4d"
  verde: "#5b7a63"
  verde-claro: "#8fae9a"
  menta: "#e4efe8"
  arena: "#f4d9b0"
  cafe: "#5b4636"
  alerta: "#8a5a2b"
  tinta-verde: "#3f5e48"
  folio: "#8a5a2b"
  escritorio: "#d6dfd9"
  papel: "#fbfaf4"
  papel-amarillo: "#fbebcf"
  papel-calculo: "#f3f8f4"
  tinta: "#1f2c35"
  tinta-tenue: "#56626b"
  tinta-carpeta: "#d3dfe6"
  tinta-carpeta-tenue: "#a9bdc9"
  filete: "rgba(31, 59, 77, 0.24)"
  filete-medio: "rgba(31, 59, 77, 0.62)"
typography:
  marca:
    fontFamily: "Barlow, Arial Narrow, system-ui, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.06em"
  headline:
    fontFamily: "Barlow, Arial Narrow, system-ui, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.01em"
  cifra:
    fontFamily: "Barlow, Arial Narrow, system-ui, sans-serif"
    fontSize: "32px"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  folio:
    fontFamily: "Barlow, Arial Narrow, system-ui, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.02em"
    fontFeature: "tnum"
  title:
    fontFamily: "Barlow, Arial Narrow, system-ui, sans-serif"
    fontSize: "15.5px"
    fontWeight: 600
    letterSpacing: "0.01em"
  body:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
  valor:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    lineHeight: 1.45
  label:
    fontFamily: "Source Sans 3, system-ui, sans-serif"
    fontSize: "12.5px"
    fontWeight: 400
    lineHeight: 1.25
  numero-casilla:
    fontFamily: "Barlow, Arial Narrow, system-ui, sans-serif"
    fontSize: "11.5px"
    fontWeight: 700
  sello:
    fontFamily: "Barlow, Arial Narrow, system-ui, sans-serif"
    fontSize: "12.5px"
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: "0.02em"
  boton:
    fontFamily: "Barlow, Arial Narrow, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    letterSpacing: "0.01em"
rounded:
  banda: "1px"
  hoja: "2px"
  radio: "3px"
  circulo: "50%"
spacing:
  filete: "1px"
  xs: "6px"
  casilla-x: "11px"
  sm: "12px"
  md: "14px"
  columna: "22px"
  hoja-x: "26px"
components:
  boton:
    backgroundColor: "{colors.tinta-verde}"
    textColor: "#ffffff"
    typography: "{typography.boton}"
    rounded: "{rounded.radio}"
    padding: "9px 16px"
  boton-hover:
    backgroundColor: "#33503c"
  boton-sec:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.navy}"
    rounded: "{rounded.radio}"
    padding: "9px 16px"
  boton-sec-hover:
    backgroundColor: "{colors.menta}"
  boton-peligro:
    backgroundColor: "{colors.alerta}"
    textColor: "#ffffff"
    rounded: "{rounded.radio}"
    padding: "9px 16px"
  boton-respuesta:
    backgroundColor: "{colors.tinta-verde}"
    textColor: "#ffffff"
    rounded: "{rounded.radio}"
    height: "58px"
    width: "100%"
  boton-respuesta-no:
    backgroundColor: "#ffffff"
    textColor: "{colors.alerta}"
    rounded: "{rounded.radio}"
    height: "58px"
    width: "100%"
  hoja:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.hoja}"
    padding: "22px 26px 30px"
  hoja-amarilla:
    backgroundColor: "{colors.papel-amarillo}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.hoja}"
    padding: "16px"
  banda:
    backgroundColor: "{colors.navy}"
    textColor: "#ffffff"
    typography: "{typography.title}"
    rounded: "{rounded.banda}"
    padding: "6px 12px"
  casilla:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    typography: "{typography.valor}"
    padding: "7px 11px 10px"
  planilla-cabeza:
    backgroundColor: "{colors.menta}"
    textColor: "{colors.navy}"
    padding: "7px 11px"
  sello:
    backgroundColor: "rgba(255, 255, 255, 0.4)"
    textColor: "{colors.navy}"
    typography: "{typography.sello}"
    rounded: "{rounded.hoja}"
    padding: "1px 7px"
  regla:
    backgroundColor: "{colors.menta}"
    textColor: "{colors.tinta-verde}"
    rounded: "{rounded.hoja}"
    padding: "0 5px"
  pestana-activa:
    backgroundColor: "{colors.escritorio}"
    textColor: "{colors.navy}"
    rounded: "3px 0 0 3px"
    padding: "10px 14px"
---

# Design System: ARKOF Despacho

## Overview

**Creative North Star: "El juego autocopiante"**

Cada incidente es un formato de campo HSE que el sistema llena solo, casilla por casilla. La interfaz no es un panel de tarjetas: es un juego de hojas autocopiantes que reposan sobre un escritorio verde gris. El original blanco pertenece a la coordinación; la copia amarilla pertenece al brigadista. La consola del coordinador es una carpeta navy con pestañas a la izquierda; cada vista es una hoja con título, membrete (Empresa / Proceso / Copia) y folio en tinta de serie.

La densidad es la de un formato real: rejillas de casillas numeradas separadas por filetes navy de 1 px, bandas navy que rotulan cada sección, planillas con cabecera menta y una bitácora al pie donde cada acción lleva hora, actor y regla (RN-xx). La jerarquía la dan la tinta y el tamaño, no las tarjetas ni las sombras. El estado de cada cosa se comunica con un sello de goma tipográfico que siempre dice su nombre; el color solo refuerza.

El sistema es de tema claro por escena: se proyecta ante el docente y se graba en video, y el brigadista lo lee a pleno sol. La UI está en español, en voz activa y sin mayúsculas sostenidas. Se rechaza de forma expresa el panel SaaS genérico de tarjetas de KPI: los indicadores son casillas del formato comparadas contra el AS-IS.

**Key Characteristics:**
- Hojas de papel (blanco para coordinación, amarillo para brigadista) sobre escritorio verde gris, con una sola sombra: la de la hoja.
- Rejillas de casillas numeradas con filetes de 1 px; el fondo del filete asoma por el hueco de la rejilla.
- Bandas navy como rótulo de sección; folios y números de casilla en tinta café rojiza.
- Sellos de estado tipográficos con doble filete; el sello grande cae (keyframe "sellar") al cambiar de estado.
- Barlow para cifras, rótulos, sellos y botones; Source Sans 3 para texto y valores.
- Cada indicador se muestra "ahora frente a antes"; cada acción se traza a su regla RN-xx.

## Colors

Paleta del documento formal (compartida con sus diagramas BPMN), trasladada a materiales de papelería: tintas oscuras sobre papeles claros, un escritorio verde gris y tres acentos semánticos (verde sistema, arena personas, alerta excepción).

### Primary
- **Navy de formato** (navy): la tinta estructural. Carpeta de la consola, bandas de sección, cabecera del portal, filete inferior de 2 px de la cabeza de hoja, títulos h1, cifras de indicadores, borde del membrete, anillo de foco y el paso actual de las fases. Los filetes de casilla son este mismo navy con transparencia (filete-medio 0.62; filete 0.24 para divisiones internas).

### Secondary
- **Tinta verde del sistema** (tinta-verde): versión oscurecida del verde del documento para que sea legible sobre papel. Botón primario, sellos de estado resuelto (confirmado, disponible, controlado, cerrado), marcador de regla RN-xx, marca de nivel 1, fases hechas y la cifra TO-BE.
- **Verde del documento** (verde): solo como relleno, nunca como texto. Barras TO-BE de la simulación y marcador de "tarea del sistema" en las fases.
- **Verde claro** (verde-claro): piloto "en vivo" del canal de notificación y cifra de mejora sobre el navy de la tapa de ingreso.
- **Menta** (menta): cabecera de planillas, hover de filas y botones secundarios, fondo de campo enfocado, fondo del marcador de regla.

### Tertiary
- **Arena de personas** (arena): lo que depende de una persona o de lo pendiente. Relleno de la marca de nivel 2, barras AS-IS, marcador de "tarea del coordinador", fondo translúcido de sellos pendientes, de la bandeja de atención y de filas marcadas; selección de texto; "Copia" sobre la cabecera navy del portal.
- **Café de tinta** (cafe): texto sobre arena. Sellos pendiente / notificado / reportado / fuera de turno, cifra "antes", borde del plazo del brigadista, rótulos de la copia amarilla.
- **Alerta ocre** (alerta): excepciones que exigen decisión. Marca de nivel 3, sellos rechazado / vencido / mantenimiento / incapacitado, bandeja de atención, banda de alerta, plazo urgente, botón de peligro y respuesta "No puedo".
- **Tinta de folio** (folio): mismo pigmento que la alerta, con papel distinto: numeración de serie de folios y números de casilla.

### Neutral
- **Escritorio verde gris** (escritorio): fondo de la aplicación, sobre el que reposan las hojas; también es el color de la pestaña activa, que se une con él como el separador de una carpeta.
- **Papel original** (papel): hojas, casillas y planillas de la coordinación.
- **Papel amarillo** (papel-amarillo): hojas y casillas de la copia del brigadista (portal y página del enlace SMS).
- **Papel de cálculo** (papel-calculo): cuerpo de la casilla 9 en vivo y del texto del SMS en la bandeja; un papel ligeramente mentolado para lo que escribe el sistema.
- **Tinta** (tinta): texto corrido y valores.
- **Tinta tenue** (tinta-tenue): rótulos de casilla, bajadas, horas y notas (≥ 5:1 sobre papel).
- **Tinta de carpeta** (tinta-carpeta / tinta-carpeta-tenue): texto sobre el navy de la carpeta y la tapa; la tenue para submarca, rol y notas.

### Named Rules
**La regla del papel y el escritorio.** Todo contenido vive sobre una hoja (papel u original amarillo); el escritorio verde gris nunca lleva contenido suelto salvo la navegación. Blanco = coordinación, amarillo = brigadista, sin excepciones.

**La regla verde-sistema, arena-personas.** Como en los diagramas del documento: verde marca lo que hace el sistema, arena lo que hace o espera una persona, alerta lo que exige una decisión. No se reasignan.

**La regla de la tinta legible.** El verde del documento (#5b7a63) no se usa como texto sobre papel; para texto, sellos y botones se usa la tinta verde (#3f5e48).

**La regla del texto siempre.** Ningún estado se comunica solo con color: todo sello, nivel, fase y bandera lleva su palabra o su número.

## Typography

**Display Font:** Barlow (con Arial Narrow, system-ui)
**Body Font:** Source Sans 3 (con system-ui)

**Character:** Barlow, estrecha e industrial, es la tinta impresa del formato: cifras, rótulos de banda, folios, sellos, botones y números de casilla. Source Sans 3 es la letra de quien llena el formato: texto, rótulos de casilla y valores. Ambas se cargan con @fontsource.

### Hierarchy
- **Marca** (700, 28px; 44px en la tapa de ingreso; 22px en móvil; interletrado 0.06em): "ARKOF" en la carpeta, la tapa y la cabecera del portal. Es tipografía, no logotipo.
- **Headline** (700, 30px, 1.1; 25px a ≤860px; 24px en la ficha del portal): título h1 de cada hoja, con text-wrap: balance.
- **Cifra** (700, 32px, 1.05; 27px a ≤860px; cifras tabulares): valor de las casillas de indicadores; unidades en small al 0.6em en tinta tenue. La cifra "antes" va en 18px café bajo filete discontinuo.
- **Folio** (700, 22px, 0.02em): número de serie en tinta de folio, precedido de "N.º" en 500 a 14px.
- **Title** (600, 15.5px): texto de bandas y encabezado de la bandeja de atención; 16–17px para subtítulos de base y convocatoria.
- **Body** (400, 15px, 1.45): texto corrido; bajadas limitadas a 68ch, notas a 60ch.
- **Valor** (600, 15px): valor dentro de la casilla; los campos editables suben a 16px para evitar el zoom en móvil.
- **Label** (400, 12.5px, 1.25, tinta tenue): rótulo de casilla, membrete y metadatos. El número de casilla (Barlow 700, 11.5px, tinta de folio) lo precede.

### Named Rules
**La regla de las dos tintas.** Barlow para lo impreso (cifras, rótulos, sellos, botones, números); Source Sans 3 para lo escrito (texto y valores). No se intercambian.

**La regla de las cifras tabulares.** Toda cifra, folio, cuenta regresiva y tabla usa font-variant-numeric: tabular-nums.

**La regla sin mayúsculas sostenidas.** Rótulos, bandas, sellos y botones van en oración; nunca text-transform: uppercase para etiquetas. La marca ARKOF es la única palabra en versales, porque es un nombre.

## Layout

El modelo espacial es un formato impreso: hojas con relleno de 22px 26px 30px, secciones rotuladas por banda, y dentro de cada sección rejillas de casillas con gap de 1px sobre fondo de filete (el filete es el hueco, no un borde). La rejilla se cierra con borde navy de 1px y sin borde superior, porque la banda hace de tapa.

- **Consola:** carpeta navy fija de 236px a la izquierda y escritorio de hasta 1240px con relleno 26px 30px 56px.
- **Primer viewport de la consola:** hoja con título y membrete; fila de cinco casillas de indicadores (subgrid de tres filas: rótulo, cifra, "antes"), bandeja de atención (o "Sin decisiones pendientes") y planilla de folios.
- **Reporte:** datos a la izquierda (1.35fr) y casilla 9 de cálculo en vivo pegajosa a la derecha (mínimo 290px).
- **Detalle:** fases en siete columnas, cuerpo 1.75fr / bitácora pegajosa (mínimo 290px), columnas separadas 22px.
- **Numeración fija de casillas:** idéntica entre reporte y detalle: 1–8 datos del reporte, 9 clasificación (nivel, brigada, kit), 10–12 tiempos y coordenadas. Un número de casilla nunca cambia de significado entre vistas.
- **Portal del brigadista:** columna única de hasta 560px, relleno lateral 12px, cabecera navy pegajosa; la banda de cada hoja se sangra a sangre sobre el borde superior de la hoja.
- **Ritmo:** 1px entre casillas; 6px entre controles pequeños; 12–14px entre bloques; 22px entre columnas y antes de secciones.

**Adaptación:**
- ≤1100px: indicadores en tres columnas (la última ocupa dos, sin hueco), reporte y detalle a una columna, se sueltan los paneles pegajosos, fases en cuatro columnas.
- ≤860px: la carpeta pasa arriba y las pestañas se vuelven horizontales con desplazamiento; cabeza de hoja apilada; indicadores y cuatro-columnas a dos; dos-columnas a una; fases a dos; ingreso a una columna.
- ≤560px: la planilla de folios pasa a renglón de dos líneas (folio, nivel y estado arriba; tipo y municipio debajo) y oculta el resto de columnas.

### Named Rules
**La regla sin hueco gris.** Una rejilla de casillas nunca deja una celda vacía que muestre el filete: la casilla huérfana se extiende a toda la fila.

## Elevation & Depth

El sistema es plano salvo por un solo material: la hoja. La profundidad se expresa con papel sobre escritorio, filetes y tinta, no con capas flotantes.

### Shadow Vocabulary
- **Sombra de hoja** (`box-shadow: 0 1px 2px rgba(31, 59, 77, 0.12), 0 8px 24px -8px rgba(31, 59, 77, 0.28)`): toda hoja, incluida la de la página del enlace SMS.
- **Respuesta al puntero** (`box-shadow: 0 2px 6px -2px rgba(31, 59, 77, 0.4)`): solo en hover del botón primario.
- **Doble aro de nivel 3** (`box-shadow: 0 0 0 2px var(--papel), 0 0 0 3.5px var(--alerta)`): un segundo aro separado por papel, no una sombra; marca la severidad máxima.
- **Halo del piloto** (`box-shadow: 0 0 0 3px` del mismo color al 18–25 %): el punto de estado del canal en la carpeta.

### Named Rules
**La regla de una sola sombra.** Solo la hoja proyecta sombra. Casillas, bandas, planillas, sellos y bandejas son planos sobre la hoja.

## Shapes

Esquinas casi rectas, como papel cortado: 1px en la tapa de las bandas, 2px en hojas, sellos, marcas de nivel, etiquetas y bandejas, 3px en botones, selectores y pestañas. Lo único redondo es el número de fase y el piloto del canal. Los bordes hacen el trabajo formal: filete de 1px (casillas, planillas), 1.5px (sellos pequeños, marca de nivel 1, casilla de sí/no), 2px (niveles 2–3, cabeza de hoja, plazo, respuesta "No puedo") y doble de 3px (sello grande). El filete discontinuo marca lo provisional o separable: el "antes" de los indicadores, el talón de la bandeja y el estado "no requerido". La única pieza girada es el sello grande (−2.5°).

## Components

### Buttons
Impresos y firmes: Barlow semibold, esquinas de 3px, sin sombra en reposo.
- **Shape:** esquinas apenas redondeadas (3px).
- **Primary:** tinta verde con texto blanco, 9px 16px; hover a #33503c con la respuesta al puntero; activo baja 1px; deshabilitado al 55 % de opacidad.
- **Secundario:** papel con texto navy y borde de filete medio; hover menta.
- **Peligro:** alerta con texto blanco; hover a #74491f.
- **Tamaños:** mini (4px 10px, 13.5px) para acciones en planilla; grande (14px 18px, 17px); ancho completo.
- **Respuestas del brigadista:** mínimo 58px de alto, 18px, ancho completo, apiladas con 10px; "No puedo" en blanco con texto y borde de 2px en alerta. Esta altura es obligatoria en el portal y en la página del enlace SMS.
- **Focus:** anillo navy de 2px con separación de 2px en todos los controles.

### Chips
- **Marcador de regla:** RN-xx en Barlow 600 11.5px, tinta verde sobre menta, esquina 2px; acompaña cada acción en bitácora y cada dato de la casilla 9.
- **Certificación:** 12px, borde de filete medio, papel translúcido.
- **Bandera "Atención":** texto alerta 11.5px con subrayado de 1.5px, junto al sello en la planilla.
- **Vía de notificación:** café sobre arena (simulada) o tinta verde sobre menta (en vivo).

### Cards / Containers
No hay tarjetas: hay hojas y casillas.
- **Hoja:** papel, borde de filete medio, esquina 2px, sombra de hoja, relleno 22px 26px 30px (16px 14px 22px a ≤860px; 16px en el portal). Variante amarilla para el brigadista.
- **Cabeza de hoja:** título y bajada a la izquierda; membrete (Empresa / Proceso / Copia, borde navy de 1px, rótulos en tinta tenue, valores en Barlow navy) y folio a la derecha; cierra con filete navy de 2px. Sin kicker ni eyebrow sobre el h1.
- **Banda:** rótulo navy de sección, Barlow 600 15.5px, nota opcional en 13.5px. Variantes tinta verde y alerta.
- **Bandeja de atención:** borde alerta, fondo arena al 50 %, filas con el motivo en café; variante tranquila en papel mentolado con título en tinta verde: "Sin decisiones pendientes".

### Inputs / Fields
- **Style:** el campo se escribe sobre la casilla: sin caja, fondo transparente, solo filete inferior de 1px, 16px semibold, esquina 0.
- **Focus:** el filete inferior pasa a navy de 2px, fondo menta translúcido y el rótulo de la casilla se vuelve navy.
- **Sí/No:** casilla cuadrada de 20px con borde navy de 1.5px que se marca con una X de dos trazos, como en papel.
- **Error:** línea con icono en alerta, semibold.

### Navigation
- **Carpeta:** navy, marca arriba, pestañas Barlow 500 15.5px en tinta de carpeta; hover blanco al 8 %; la pestaña activa toma el color del escritorio, texto navy 700, y se une con la hoja como separador de carpeta. Pie con piloto del canal, usuario y acciones con borde blanco al 22 %.
- **Móvil (≤860px):** la carpeta se vuelve franja superior; las pestañas se desplazan en horizontal con esquinas superiores de 3px.
- **Portal:** cabecera navy pegajosa con la marca y la etiqueta "Copia" en arena.

### Sello de estado
El componente firma del sistema. Barlow 700 12.5px, borde de 1.5px del color de la tinta, fondo blanco al 40 %, esquina 2px, siempre con texto. Tintas por familia: tinta verde (confirmado, disponible, controlado, cerrado), café sobre arena (pendiente, notificado, reportado, fuera de turno), alerta (rechazado, vencido, mantenimiento, incapacitado), navy (reservado, asignado, en ruta, en sitio), tinta tenue con borde discontinuo (no requerido). El **sello grande** (17px, doble filete de 3px, girado −2.5°) cae con el keyframe "sellar" (260ms, cubic-bezier(0.16, 1, 0.3, 1): de −6° y escala 1.35 con desenfoque a −2.5° y escala 1) cada vez que el estado cambia; con movimiento reducido aparece quieto.

### Marca de nivel
La escala es la severidad: n1 de 22px con contorno de tinta verde; n2 de 26px en café sobre arena con borde de 2px; n3 de 30px relleno en alerta con texto blanco y doble aro. En la casilla 9 y la convocatoria crece a 38px. Puede llevar el rótulo "Nivel".

### Casilla de indicador
Cinco casillas en subgrid (rótulo, cifra, "antes"), la cifra actual en navy y la referencia AS-IS debajo en café tras filete discontinuo. Así se leen "ahora frente a antes" alineadas en toda la fila.

### Casilla 9 en vivo
Panel de cálculo pegajoso con banda, cuerpo en papel de cálculo, marca de nivel grande y lista de nivel, brigada y kit, cada dato con su marcador RN-xx; se recalcula mientras se llena el reporte.

### Fases, bitácora y planilla
- **Fases:** siete celdas en rejilla de filete; hechas en tinta verde con número relleno, la actual en navy invertido; cada fase indica si la hace el sistema (marcador verde) o el coordinador (marcador arena).
- **Bitácora:** hora (84px) + tipo en Barlow navy + detalle + meta con marcador de regla; filas de alerta en arena translúcido.
- **Planilla:** cabecera Barlow 600 13px navy sobre menta con filete navy de 1.5px; filas de 14px con filete tenue; hover y foco en menta; filas que exigen decisión en arena translúcido.
- **Plazo del brigadista:** caja blanca con borde café de 2px y cuenta regresiva Barlow 34px; pasa a alerta cuando urge.

## Do's and Don'ts

### Do:
- **Do** poner todo contenido sobre una hoja con la sombra de hoja; papel blanco para la coordinación, amarillo para el brigadista.
- **Do** separar casillas con gap de 1px sobre fondo de filete medio y numerarlas con Barlow 700 en tinta de folio.
- **Do** conservar la numeración de casillas idéntica entre reporte y detalle: 1–8 datos, 9 clasificación, 10–12 tiempos y coordenadas.
- **Do** rotular cada sección con una banda navy (tinta verde o alerta solo cuando la sección es del sistema o una excepción).
- **Do** acompañar todo estado con su palabra en un sello; el color solo refuerza.
- **Do** escalar tamaño y tinta con la severidad en la marca de nivel (n1 contorno verde, n2 arena, n3 alerta con doble aro).
- **Do** mostrar cada indicador frente a su valor AS-IS y cada acción con su regla RN-xx.
- **Do** dar a las respuestas del brigadista al menos 58px de alto y ancho completo.
- **Do** usar iconos SVG de un solo trazo (1.75) en currentColor.
- **Do** respetar prefers-reduced-motion: sin transiciones ni caída del sello.

### Don't:
- **Don't** construir tarjetas de KPI ni paneles SaaS de tarjetas: los indicadores son casillas del formato.
- **Don't** poner kicker ni eyebrow sobre los h1; el membrete y el folio ya contextualizan la hoja.
- **Don't** comunicar un estado solo con color.
- **Don't** usar mayúsculas sostenidas en rótulos, bandas, sellos o botones.
- **Don't** usar el verde del documento (#5b7a63) como color de texto sobre papel.
- **Don't** dar sombra a casillas, bandas, planillas o sellos; la única sombra es la de la hoja.
- **Don't** pasar a tema oscuro: la escena es proyección, video y sol de campo.
- **Don't** inventar un logotipo de ARKOF; la marca es la palabra en Barlow.
- **Don't** girar otra pieza que no sea el sello grande.
