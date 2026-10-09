import { useEffect, useState } from "react";
import { enviar } from "./api.js";
import {
  CabezaHoja, Casilla, CANAL, CERT, CICLO, EQUIPO, ETIQUETA, ESTADO_RECURSO, Icono, Nivel, ROL, Sello, TIPOS,
  dur, fechaHora, hora, num, reglasCitadas, reloj, restante, useAhora, useSondeo,
} from "./comunes.jsx";

const SIGUIENTE = { confirmado: "en_ruta", en_ruta: "en_sitio", en_sitio: "controlado" };
const MUNICIPIOS = {
  "Villavicencio": [4.153, -73.635], "Acacías": [3.99, -73.76], "Puerto López": [4.085, -72.957],
  "Puerto Gaitán": [4.314, -72.082], "Castilla La Nueva": [3.83, -73.69], "Yopal": [5.337, -72.395], "Tauramena": [5.018, -72.747],
};
// Quién mueve cada fase del ciclo (figura 6 del documento).
const RESPONSABLE = { reportado: "sistema", notificado: "sistema", confirmado: "sistema", en_ruta: "coordinador", en_sitio: "coordinador", controlado: "coordinador", cerrado: "coordinador" };
const MARCA_TIEMPO = { reportado: "reportado_en", notificado: "notificado_en", confirmado: "confirmado_en", en_sitio: "en_sitio_en", cerrado: "cerrado_en" };

// Rótulos de la bitácora (RN-11) con la ortografía del documento.
const TIPO_EVENTO = {
  REPORTE: "Reporte", CLASIFICACION: "Clasificación", ASIGNACION: "Asignación", RESERVA_EQUIPOS: "Reserva de equipos",
  NOTIFICACION: "Notificación", ALERTA_RECURSOS: "Alerta de recursos", RESPUESTA_BRIGADISTA: "Respuesta del brigadista",
  BRIGADA_CONFIRMADA: "Brigada confirmada", SIN_REEMPLAZO_NECESARIO: "Sin reemplazo necesario", ESCALAMIENTO: "Reemplazo automático",
  SLA_VENCIDO: "Plazo vencido", ESCALAMIENTO_HUMANO: "Escalamiento al coordinador", CAMBIO_ESTADO: "Cambio de estado",
  CIERRE: "Cierre", INFORME: "Informe al cliente", CONVOCATORIA_CON_FATIGA: "Convocatoria con fatiga",
};
const ACTOR = { sistema: "Sistema", n8n: "n8n", coordinador: "Coordinador", cliente: "Cliente" };

const requiereDecision = (i) => i.estado !== "cerrado" && (i.recursos_insuficientes || i.rondas_escalamiento > 2 || i.convocado_con_fatiga);
const motivoDecision = (i) => i.recursos_insuficientes ? "Recursos insuficientes: active la ayuda mutua o reasigne (RN-09)"
  : i.rondas_escalamiento > 2 ? "Superó las rondas automáticas de reemplazo (RN-08)"
  : "Se convocó a personal con fatiga: confirme o active la ayuda mutua (RN-04)";

export default function Consola({ usuario, alSalir }) {
  const [vista, setVista] = useState("tablero");
  const [incidenteId, setIncidenteId] = useState(null);
  const [salud] = useSondeo("/api/salud", 15000);
  const abrir = (id) => { setIncidenteId(id); setVista("detalle"); window.scrollTo(0, 0); };
  const ir = (v) => { setVista(v); window.scrollTo(0, 0); };
  const menu = [["tablero", "Tablero de operación"], ["reportar", "Reportar incidente"], ["recursos", "Brigadistas y equipos"], ["bandeja", "Notificaciones"]];

  const reiniciar = async () => {
    if (!window.confirm("Se borrarán los incidentes y se restaurarán los brigadistas y equipos de la semilla. ¿Continuar?")) return;
    await enviar("/api/demo/reiniciar");
    ir("tablero");
  };

  return (
    <div className="consola">
      <nav className="carpeta" aria-label="Navegación principal">
        <div className="carpeta-marca">
          <p className="marca">ARKOF</p>
          <p className="submarca">Despacho de brigadas</p>
        </div>
        <ul className="pestanas">
          {menu.map(([k, t]) => {
            const activa = vista === k || (k === "tablero" && vista === "detalle");
            return <li key={k}><button className={activa ? "activa" : ""} aria-current={activa ? "page" : undefined} onClick={() => ir(k)}>{t}</button></li>;
          })}
        </ul>
        <div className="carpeta-pie">
          <p className="canal-estado">
            <span className={`punto ${salud?.n8n ? "vivo" : ""}`} aria-hidden="true" />
            {salud?.n8n ? "Notificaciones vía n8n" : "Modo simulación (sin n8n)"}
          </p>
          <p className="quien"><b>{usuario.nombre}</b><span>Coordinador · {usuario.usuario}</span></p>
          <div className="carpeta-acciones">
            <button onClick={reiniciar} title="Restaura los datos de demostración"><Icono nombre="reiniciar" />Reiniciar demo</button>
            <button onClick={alSalir}><Icono nombre="salir" />Salir</button>
          </div>
        </div>
      </nav>
      <main className="escritorio">
        {vista === "tablero" && <Tablero abrir={abrir} ir={ir} />}
        {vista === "reportar" && <Reportar creado={abrir} />}
        {vista === "detalle" && incidenteId && <Detalle id={incidenteId} volver={() => ir("tablero")} />}
        {vista === "recursos" && <Recursos />}
        {vista === "bandeja" && <Bandeja n8n={salud?.n8n} />}
      </main>
    </div>
  );
}

/* ------------------------------------------------------------------ Tablero */
function Tablero({ abrir, ir }) {
  const [k] = useSondeo("/api/kpis");
  const [lista] = useSondeo("/api/incidentes");
  const [sim] = useSondeo("/api/simulacion", 600000);
  const atencion = (lista || []).filter(requiereDecision);
  const confirmadoMin = k?.min_prom_reporte_a_brigada_confirmada;

  return (
    <article className="hoja">
      <CabezaHoja titulo="Tablero de operación" copia="Original, coordinación HSE"
        bajada="Indicadores en tiempo real frente a la línea base del proceso manual (capítulo 2) e incidentes en curso." />

      <section aria-labelledby="t-indicadores">
        <h2 className="banda" id="t-indicadores">Indicadores del turno</h2>
        <div className="casillas indicadores">
          <Casilla n={1} rotulo="Reporte → brigada notificada">
            <span className="cifra">{k ? dur(k.seg_prom_reporte_a_notificacion) : "—"}</span>
            <span className="antes">Antes <b>10–15 min</b> solo verificando por teléfono</span>
          </Casilla>
          <Casilla n={2} rotulo="Reporte → brigada confirmada">
            <span className="cifra">{confirmadoMin == null ? "—" : dur(confirmadoMin * 60)}</span>
            <span className="antes">Antes <b>25–40 min</b> hasta el despacho</span>
          </Casilla>
          <Casilla n={3} rotulo="Reemplazos resueltos por el sistema, sin llamadas">
            <span className="cifra">{k ? `${num(k.tasa_reasignacion_pct)} %` : "—"}</span>
            <span className="antes">Antes <b>0 %</b> automático: cada reproceso, por teléfono</span>
          </Casilla>
          <Casilla n={4} rotulo="Cierres con trazabilidad completa">
            <span className="cifra">{k?.trazabilidad_completa_pct == null ? "—" : `${num(k.trazabilidad_completa_pct, 0)} %`}</span>
            <span className="antes">Antes <b>parcial</b> en cuaderno o Excel</span>
          </Casilla>
          <Casilla n={5} rotulo="Brigadistas disponibles">
            <span className="cifra">{k ? <>{k.brigadistas_disponibles}<small>/{k.brigadistas_totales}</small></> : "—"}</span>
            <span className="antes">{k ? <>Equipos libres <b>{k.equipos_disponibles}/{k.equipos_totales}</b></> : ""}</span>
          </Casilla>
        </div>
      </section>

      {lista && atencion.length === 0 && (
        <section className="atencion tranquila" aria-labelledby="t-atencion">
          <h2 id="t-atencion"><Icono nombre="check" />Sin decisiones pendientes</h2>
          <p>El sistema resolvió todos los despachos. Aquí aparecerán los casos que exijan su decisión: recursos insuficientes (RN-09), rondas de reemplazo agotadas (RN-08) o personal convocado con fatiga (RN-04).</p>
        </section>
      )}
      {atencion.length > 0 && (
        <section className="atencion" aria-labelledby="t-atencion">
          <h2 id="t-atencion"><Icono nombre="alerta" />Requieren su decisión ({atencion.length})</h2>
          <ul>
            {atencion.map((i) => (
              <li key={i.id}>
                <button onClick={() => abrir(i.id)}>
                  <b className="folio-mini">{i.codigo}</b>
                  <span>{motivoDecision(i)}</span>
                  <Icono nombre="flecha" className="girar" />
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-labelledby="t-incidentes">
        <h2 className="banda" id="t-incidentes">Incidentes</h2>
        {lista && lista.length === 0 && (
          <div className="vacio">
            <p><b>Aún no hay incidentes en este turno.</b> Al registrar uno, el sistema lo clasifica, propone la brigada, reserva el kit y notifica en milisegundos.</p>
            <button className="boton" onClick={() => ir("reportar")}>Reportar un incidente</button>
          </div>
        )}
        {lista && lista.length > 0 && (
          <div className="desliza">
            <table className="planilla folios">
              <thead><tr><th>Folio</th><th>Nivel</th><th>Tipo</th><th>Cliente</th><th>Municipio</th><th>Estado</th><th className="der">Reportado</th><th className="der">Hasta confirmar</th></tr></thead>
              <tbody>
                {lista.map((i) => (
                  <tr key={i.id} className={`clic${requiereDecision(i) ? " marcada" : ""}`} onClick={() => abrir(i.id)} tabIndex={0}
                    onKeyDown={(e) => e.key === "Enter" && abrir(i.id)} aria-label={`Abrir ${i.codigo}`}>
                    <td><b className="folio-mini">{i.codigo}</b></td>
                    <td><Nivel n={i.nivel} /></td>
                    <td data-municipio={i.municipio}>{TIPOS[i.tipo]}</td>
                    <td className="tenue">{i.empresa}</td>
                    <td>{i.municipio}</td>
                    <td><Sello estado={i.estado} />{requiereDecision(i) && <span className="bandera">Atención</span>}</td>
                    <td className="der num">{hora(i.reportado_en)}</td>
                    <td className="der num">{dur(i.seg_reporte_a_confirmacion)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {sim?.disponible && <Simulacion s={sim} />}
    </article>
  );
}

function Simulacion({ s }) {
  const max = Math.max(...Object.values(s.por_nivel).map((v) => v.asis));
  const mejora = Math.round((1 - s.tobe_media / s.asis_media) * 1000) / 10;
  return (
    <section aria-labelledby="t-sim">
      <h2 className="banda" id="t-sim">Evidencia: simulación de {s.n} incidentes</h2>
      <div className="sim">
        <div className="sim-resumen">
          <p className="sim-cifra"><span className="tachado">{num(s.asis_media)}</span><Icono nombre="flecha" className="girar" /><b>{num(s.tobe_media)} min</b></p>
          <p>Tiempo medio del reporte a la brigada despachada (AS-IS) o confirmada (TO-BE): <b>−{num(mejora)} %</b>. Percentil 90: {num(s.asis_p90)} → {num(s.tobe_p90)} min.</p>
          <p>{num(s.sin_intervencion_pct)} % de los incidentes se resolvieron sin intervención manual. Despachos con recurso no disponible: {num(s.despacho_erroneo_asis_pct, 0)} % → {num(s.despacho_erroneo_tobe_pct, 0)} %.</p>
          <p className="fuente">Fuente: <code>backend/resultados_simulacion.json</code>, sección 6.8 del documento.</p>
        </div>
        <figure className="barras" aria-label="Tiempo medio por nivel, proceso manual frente al sistema">
          <figcaption>
            <span><i className="muestra asis" />Proceso manual (personas)</span>
            <span><i className="muestra tobe" />Con el sistema</span>
          </figcaption>
          {Object.entries(s.por_nivel).map(([n, v]) => (
            <div className="barra-fila" key={n}>
              <Nivel n={Number(n)} />
              <div className="barra-par">
                <div className="barra asis" style={{ width: `${(v.asis / max) * 100}%` }}><span>{num(v.asis)} min</span></div>
                <div className="barra tobe" style={{ width: `${(v.tobe / max) * 100}%` }}><span>{num(v.tobe)} min</span></div>
              </div>
            </div>
          ))}
          <p className="barras-nota">El manual crece con el tamaño de la brigada porque las llamadas son en serie; el sistema notifica a todos a la vez.</p>
        </figure>
      </div>
    </section>
  );
}

/* ------------------------------------------------------------------ Reportar */
function Reportar({ creado }) {
  const [empresas] = useSondeo("/api/empresas", 60000);
  const [f, setF] = useState({
    empresa_id: 1, canal: "telefono", tipo: "DERRAME_HIDROCARBURO", municipio: "Acacías",
    volumen_bbl: 3, cuerpo_agua: false, comunidad_cercana: false, descripcion: "",
  });
  const [previa, setPrevia] = useState(null);
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const cambiar = (c) => (e) => setF({ ...f, [c]: e.target.value });
  const marcar = (c, v) => setF({ ...f, [c]: v });

  // Casilla 9: el motor aplica las reglas en vivo mientras se llena el formato (sin registrar nada).
  useEffect(() => {
    const t = setTimeout(() => {
      enviar("/api/incidentes/previsualizar", { tipo: f.tipo, volumen_bbl: Number(f.volumen_bbl) || 0, cuerpo_agua: f.cuerpo_agua, comunidad_cercana: f.comunidad_cercana })
        .then(setPrevia).catch(() => setPrevia(null));
    }, 150);
    return () => clearTimeout(t);
  }, [f.tipo, f.volumen_bbl, f.cuerpo_agua, f.comunidad_cercana]);

  const registrar = async (e) => {
    e.preventDefault(); setError(null); setEnviando(true);
    const [lat, lon] = MUNICIPIOS[f.municipio];
    try {
      const inc = await enviar("/api/incidentes", { ...f, empresa_id: Number(f.empresa_id), volumen_bbl: Number(f.volumen_bbl) || 0, lat, lon, actor: "coordinador" });
      creado(inc.id);
    } catch (err) { setError(err.message); } finally { setEnviando(false); }
  };

  return (
    <form className="hoja" onSubmit={registrar}>
      <CabezaHoja titulo="Reporte de incidente ambiental" copia="Original, coordinación HSE"
        bajada="Digite el reporte que llega por teléfono o revise el del portal. Al registrarlo, el sistema clasifica, asigna, reserva y notifica sin llamadas." />
      <div className="reporte">
        <section aria-labelledby="r-datos">
          <h2 className="banda" id="r-datos">Datos del reporte</h2>
          <div className="casillas dos-col">
            <label className="casilla campo">
              <span className="casilla-rotulo"><span className="casilla-n">1</span>Empresa afiliada</span>
              <select value={f.empresa_id} onChange={cambiar("empresa_id")}>{empresas?.map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}</select>
            </label>
            <label className="casilla campo">
              <span className="casilla-rotulo"><span className="casilla-n">2</span>Canal del reporte</span>
              <select value={f.canal} onChange={cambiar("canal")}>{Object.entries(CANAL).map(([k, t]) => <option key={k} value={k}>{t}</option>)}</select>
            </label>
            <label className="casilla campo">
              <span className="casilla-rotulo"><span className="casilla-n">3</span>Tipo de incidente</span>
              <select value={f.tipo} onChange={cambiar("tipo")}>{Object.entries(TIPOS).map(([k, t]) => <option key={k} value={k}>{t}</option>)}</select>
            </label>
            <label className="casilla campo">
              <span className="casilla-rotulo"><span className="casilla-n">4</span>Municipio</span>
              <select value={f.municipio} onChange={cambiar("municipio")}>{Object.keys(MUNICIPIOS).map((m) => <option key={m}>{m}</option>)}</select>
            </label>
            <label className="casilla campo">
              <span className="casilla-rotulo"><span className="casilla-n">5</span>Volumen estimado</span>
              <span className="con-unidad"><input type="number" min="0" step="0.5" inputMode="decimal" value={f.volumen_bbl} onChange={cambiar("volumen_bbl")} /><span>barriles</span></span>
            </label>
            <SiNo n={6} rotulo="Cuerpo de agua afectado o en riesgo" nombre="cuerpo_agua" valor={f.cuerpo_agua} alCambiar={(v) => marcar("cuerpo_agua", v)} />
            <SiNo n={7} rotulo="Comunidad cercana expuesta" nombre="comunidad_cercana" valor={f.comunidad_cercana} alCambiar={(v) => marcar("comunidad_cercana", v)} />
            <label className="casilla campo ancho">
              <span className="casilla-rotulo"><span className="casilla-n">8</span>Descripción</span>
              <textarea rows="3" value={f.descripcion} onChange={cambiar("descripcion")} placeholder="Qué ocurrió, punto de referencia, acceso al sitio…" />
            </label>
          </div>
        </section>

        <section className="calculo" aria-labelledby="r-calculo" aria-live="polite">
          <h2 className="banda verde" id="r-calculo">Lo que hará el sistema</h2>
          <div className="casilla calculo-cuerpo">
            <div className="casilla-rotulo"><span className="casilla-n">9</span>Clasificación y despacho (se calcula mientras escribe)</div>
            {previa ? (
              <>
                <div className="calculo-nivel"><Nivel n={previa.nivel} conTexto /><p>Asignado por RN-01 según volumen, sustancia, agua y comunidad.</p></div>
                <dl className="calculo-lista">
                  <div><dt>Brigada</dt><dd>{previa.brigada} personas, {previa.lideres} {previa.lideres === 1 ? "líder" : "líderes"}{previa.sobreconvocatoria > 0 && ` + ${previa.sobreconvocatoria} en sobre-convocatoria`}</dd><dd className="regla">RN-02 · RN-07b</dd></div>
                  <div><dt>Certificación</dt><dd>{CERT[previa.certificacion]}</dd><dd className="regla">RN-03</dd></div>
                  <div><dt>Plazo para confirmar</dt><dd>{num(previa.sla_minutos, 0)} min por brigadista</dd><dd className="regla">RN-07</dd></div>
                  <div><dt>Kit a reservar</dt><dd>{Object.entries(previa.kit).map(([t, c]) => `${c} × ${EQUIPO[t]}`).join(" · ")}</dd><dd className="regla">RN-05 · RN-06</dd></div>
                </dl>
              </>
            ) : <p className="tenue">Calculando…</p>}
          </div>
          {error && <p className="error" role="alert"><Icono nombre="alerta" />{error}</p>}
          <button className="boton ancho grande" disabled={enviando}>{enviando ? "Despachando…" : "Registrar y despachar"}</button>
        </section>
      </div>
    </form>
  );
}

// Casilla de marcar Sí / No, como en los formatos impresos.
function SiNo({ n, rotulo, nombre, valor, alCambiar }) {
  return (
    <fieldset className="casilla campo sino">
      <legend className="casilla-rotulo"><span className="casilla-n">{n}</span>{rotulo}</legend>
      <div className="opciones">
        {[[true, "Sí"], [false, "No"]].map(([v, t]) => (
          <label key={t} className={valor === v ? "marcada" : ""}>
            <input type="radio" name={nombre} checked={valor === v} onChange={() => alCambiar(v)} />
            <span className="caja" aria-hidden="true" />{t}
          </label>
        ))}
      </div>
    </fieldset>
  );
}

/* ------------------------------------------------------------------ Detalle */
function Detalle({ id, volver }) {
  const [inc, recargar] = useSondeo(`/api/incidentes/${id}`, 2000);
  const [notas, setNotas] = useState("");
  const [error, setError] = useState(null);
  const ahora = useAhora();
  if (!inc) return <article className="hoja"><p className="tenue">Cargando el formato del incidente…</p></article>;

  const idx = CICLO.indexOf(inc.estado);
  const accion = async (ruta, cuerpo) => {
    setError(null);
    try { await enviar(ruta, cuerpo); recargar(); } catch (e) { setError(e.message); }
  };
  const responder = (token, si) => fetch(`/confirmar/${token}`, { method: "POST", body: new URLSearchParams({ respuesta: si ? "si" : "no" }) }).then(recargar);
  const confirmados = inc.asignaciones.filter((a) => a.estado === "confirmado").length;
  const nombres = Object.fromEntries(inc.asignaciones.map((a) => [`brigadista:${a.brigadista_id}`, a.brigadista]));
  const nombreActor = (actor) => nombres[actor] || ACTOR[actor] || actor;

  return (
    <article className="hoja">
      <button className="volver" onClick={volver}><Icono nombre="flecha" />Volver al tablero</button>
      <CabezaHoja titulo={TIPOS[inc.tipo]} folio={inc.codigo} copia="Original, coordinación HSE"
        bajada={`${inc.municipio} · ${inc.empresa}`}>
        <div className="cabeza-sellos"><Nivel n={inc.nivel} conTexto /><Sello key={inc.estado} estado={inc.estado} grande /></div>
      </CabezaHoja>

      {inc.recursos_insuficientes && inc.estado !== "cerrado" && (
        <div className="atencion en-linea" role="status"><Icono nombre="alerta" />
          <p><b>Recursos insuficientes para completar la brigada o el kit (RN-09).</b> Decisión del coordinador: activar el convenio de ayuda mutua o reasignar manualmente.</p>
        </div>
      )}
      {inc.convocado_con_fatiga && inc.estado !== "cerrado" && (
        <div className="atencion en-linea" role="status"><Icono nombre="alerta" />
          <p><b>Se convocó a personal con fatiga porque no había alternativa descansada (RN-04).</b> Revise la bitácora y decida si continúa o activa la ayuda mutua.</p>
        </div>
      )}
      {error && <p className="error" role="alert"><Icono nombre="alerta" />{error}</p>}

      <section aria-labelledby="d-datos">
        <h2 className="banda" id="d-datos">Datos del reporte</h2>
        <div className="casillas cuatro">
          {/* Misma numeración que el formato de reporte: una casilla, un número en todas las copias */}
          <Casilla n={1} rotulo="Empresa afiliada">{inc.empresa}</Casilla>
          <Casilla n={2} rotulo="Canal del reporte">{CANAL[inc.canal] || inc.canal}</Casilla>
          <Casilla n={3} rotulo="Tipo de incidente">{TIPOS[inc.tipo]}</Casilla>
          <Casilla n={4} rotulo="Municipio">{inc.municipio}</Casilla>
          <Casilla n={5} rotulo="Volumen estimado">{num(inc.volumen_bbl)} barriles</Casilla>
          <Casilla n={6} rotulo="Cuerpo de agua">{inc.cuerpo_agua ? "Sí, afectado o en riesgo" : "No"}</Casilla>
          <Casilla n={7} rotulo="Comunidad cercana" className="doble">{inc.comunidad_cercana ? "Sí, expuesta" : "No"}</Casilla>
          <Casilla n={8} rotulo="Descripción" className="ancho">{inc.descripcion || <span className="tenue">Sin descripción</span>}</Casilla>
          <Casilla n={9} rotulo="Clasificación (RN-01)"><Nivel n={inc.nivel} conTexto /></Casilla>
          <Casilla n={10} rotulo="Reportado">{fechaHora(inc.reportado_en)}</Casilla>
          <Casilla n={11} rotulo="Reporte → notificación">{dur(inc.seg_reporte_a_notificacion)}</Casilla>
          <Casilla n={12} rotulo="Coordenadas">{inc.lat.toFixed(4)}, {inc.lon.toFixed(4)}</Casilla>
        </div>
      </section>

      <section aria-labelledby="d-ciclo">
        <h2 className="banda" id="d-ciclo">Ciclo de vida</h2>
        <ol className="fases">
          {CICLO.map((e, i) => (
            <li key={e} className={i < idx ? "hecha" : i === idx ? "actual" : ""} aria-current={i === idx ? "step" : undefined}>
              <span className="fase-n">{i < idx ? <Icono nombre="check" tam={14} /> : i + 1}</span>
              <span className="fase-nombre">{ETIQUETA[e]}</span>
              <span className={`fase-quien ${RESPONSABLE[e]}`}>{RESPONSABLE[e]}</span>
              {MARCA_TIEMPO[e] && inc[MARCA_TIEMPO[e]] && <span className="fase-hora num">{hora(inc[MARCA_TIEMPO[e]])}</span>}
            </li>
          ))}
        </ol>
      </section>

      <div className="detalle-cuerpo">
        <div>
          <section aria-labelledby="d-brigada">
            <h2 className="banda" id="d-brigada">Brigada <span className="banda-nota">{confirmados} de {inc.brigada_requerida} confirmados · plazo {num(inc.sla_minutos, 0)} min</span></h2>
            <div className="desliza">
              <table className="planilla">
                <thead><tr><th>Brigadista</th><th>Rol</th><th className="der">Distancia</th><th>Estado</th><th>Plazo o respuesta</th><th><span className="solo-lector">Acciones</span></th></tr></thead>
                <tbody>
                  {inc.asignaciones.map((a) => {
                    const s = restante(a.vence_en, ahora);
                    return (
                      <tr key={a.id}>
                        <td><b>{a.brigadista}</b></td>
                        <td>{ROL[a.rol_en_brigada]}</td>
                        <td className="der num">{num(a.distancia_km)} km</td>
                        <td><Sello estado={a.estado} /></td>
                        <td className="num">{a.estado === "pendiente"
                          ? <span className={`cuenta${s <= 60 ? " urge" : ""}`}><Icono nombre="reloj" tam={15} />{s > 0 ? reloj(s) : "venció, esperando verificación"}</span>
                          : hora(a.respondido_en)}</td>
                        <td>
                          <span className="acciones">
                            {a.estado === "pendiente" && <>
                              <button className="boton mini" onClick={() => responder(a.token, true)} title="Simula la respuesta del brigadista desde su celular">Confirma</button>
                              <button className="boton mini sec" onClick={() => responder(a.token, false)} title="Simula un rechazo del brigadista">Rechaza</button>
                            </>}
                            <a className="boton mini sec" href={`/confirmar/${a.token}`} target="_blank" rel="noopener noreferrer"
                              title="Abre en una pestaña nueva la página que recibe el brigadista por correo y SMS">Ver como brigadista<Icono nombre="enlace" tam={14} /></a>
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          <section aria-labelledby="d-equipos">
            <h2 className="banda" id="d-equipos">Kit reservado</h2>
            {inc.equipos.length === 0 ? <p className="tenue relleno">No se reservaron equipos.</p> : (
              <ul className="kit">
                {inc.equipos.map((e) => (
                  <li key={e.id}><b className="num">{e.codigo}</b><span>{e.descripcion}</span><span className="tenue">{e.base}</span>
                    {e.liberado ? <Sello estado="disponible" texto="Liberado" /> : <Sello estado={e.estado} />}</li>
                ))}
              </ul>
            )}
          </section>

          <section aria-labelledby="d-acciones">
            <h2 className="banda" id="d-acciones">Acciones del coordinador</h2>
            <div className="acciones-coord">
              {SIGUIENTE[inc.estado] && <button className="boton" onClick={() => accion(`/api/incidentes/${id}/estado`, { estado: SIGUIENTE[inc.estado] })}>Marcar “{ETIQUETA[SIGUIENTE[inc.estado]]}”</button>}
              {inc.estado === "notificado" && <button className="boton sec" onClick={() => accion(`/api/incidentes/${id}/verificar-sla`, { forzar: true })}>Forzar vencimiento del plazo (demo)</button>}
              {inc.estado !== "cerrado" && (
                <div className="cierre">
                  <label className="casilla campo">
                    <span className="casilla-rotulo">Notas de cierre</span>
                    <textarea rows="2" value={notas} onChange={(e) => setNotas(e.target.value)} placeholder="Acciones de contención, disposición de residuos, novedades…" />
                  </label>
                  <button className="boton peligro" onClick={() => accion(`/api/incidentes/${id}/estado`, { estado: "cerrado", notas })}>Cerrar y enviar informe al cliente</button>
                </div>
              )}
              {inc.estado === "cerrado" && <a className="boton sec" href={`/api/incidentes/${id}/informe`} target="_blank" rel="noreferrer"><Icono nombre="documento" />Ver informe de trazabilidad</a>}
            </div>
          </section>
        </div>

        <section className="bitacora-caja" aria-labelledby="d-bitacora">
          <h2 className="banda" id="d-bitacora">Bitácora de trazabilidad</h2>
          <ol className="bitacora">
            {inc.eventos.map((e) => {
              const { limpio, reglas } = reglasCitadas(e.detalle);
              const alerta = /ALERTA|VENCIDO|ESCALAMIENTO|FATIGA/.test(e.tipo);
              return (
                <li key={e.id} className={alerta ? "alerta" : ""}>
                  <span className="b-hora num">{hora(e.momento)}</span>
                  <div>
                    <p className="b-tipo">{TIPO_EVENTO[e.tipo] || e.tipo.replaceAll("_", " ").toLowerCase()}{alerta && <span className="bandera">Atención</span>}</p>
                    <p className="b-detalle">{limpio}</p>
                    <p className="b-meta"><span>{nombreActor(e.actor)}</span>{reglas && <span className="regla">{reglas}</span>}</p>
                  </div>
                </li>
              );
            })}
          </ol>
        </section>
      </div>
    </article>
  );
}

/* ------------------------------------------------------------------ Recursos */
function Recursos() {
  const [brig, recB] = useSondeo("/api/brigadistas", 5000);
  const [eq, recE] = useSondeo("/api/equipos", 5000);
  const estadoB = (b, estado) => enviar(`/api/brigadistas/${b.id}`, { estado }, "PATCH").then(recB);
  const estadoE = (e, estado) => enviar(`/api/equipos/${e.id}`, { estado }, "PATCH").then(recE);
  const porBase = eq && eq.reduce((acc, e) => {
    (acc[e.base] ||= {});
    (acc[e.base][e.tipo] ||= []).push(e);
    return acc;
  }, {});

  return (
    <article className="hoja">
      <CabezaHoja titulo="Brigadistas y equipos" copia="Original, coordinación HSE"
        bajada="Fuente única de disponibilidad: reemplaza las llamadas de verificación. El motor solo convoca a quien figura como disponible aquí." />
      <section aria-labelledby="rc-personal">
        <h2 className="banda" id="rc-personal">Planilla de personal</h2>
        <div className="desliza">
          <table className="planilla">
            <thead><tr><th>Nombre</th><th>Usuario</th><th>Rol</th><th>Base</th><th>Certificaciones</th><th className="der">Atenciones 24 h</th><th>Estado</th><th>Cambiar</th></tr></thead>
            <tbody>{brig?.map((b) => (
              <tr key={b.id}>
                <td><b>{b.nombre}</b></td>
                <td className="num tenue">{b.usuario}</td>
                <td>{ROL[b.rol]}</td>
                <td>{b.base}</td>
                <td><span className="certs">{b.certificaciones.map((c) => <span key={c} className="cert">{CERT[c] || c}</span>)}</span></td>
                <td className="der num">{b.atenciones_24h}</td>
                <td><Sello estado={b.estado} /></td>
                <td><select className="selector" value={b.estado} onChange={(e) => estadoB(b, e.target.value)} aria-label={`Estado de ${b.nombre}`}>
                  {["disponible", "asignado", "fuera_turno", "incapacitado"].map((s) => <option key={s} value={s}>{ESTADO_RECURSO[s]}</option>)}</select></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </section>

      <section aria-labelledby="rc-equipos">
        <h2 className="banda" id="rc-equipos">Inventario por base</h2>
        <p className="leyenda">
          <span><i className="unidad disponible" />Disponible</span>
          <span><i className="unidad reservado" />Reservado para un incidente</span>
          <span><i className="unidad mantenimiento" />En mantenimiento</span>
          <span className="tenue">Toque una unidad libre para enviarla a mantenimiento o devolverla.</span>
        </p>
        <div className="bases">
          {porBase && Object.entries(porBase).map(([base, tipos]) => (
            <div className="base" key={base}>
              <h3>{base}</h3>
              <dl>
                {Object.entries(tipos).map(([tipo, unidades]) => (
                  <div key={tipo} className="base-fila">
                    <dt>{EQUIPO[tipo]} <span className="tenue">{unidades.filter((u) => u.estado === "disponible").length} de {unidades.length}</span></dt>
                    <dd>{unidades.map((u) => (
                      <button key={u.id} className={`unidad ${u.estado}`} disabled={u.estado === "reservado"}
                        title={`${u.codigo}: ${ESTADO_RECURSO[u.estado]}`} aria-label={`${u.codigo}, ${ESTADO_RECURSO[u.estado]}`}
                        onClick={() => estadoE(u, u.estado === "mantenimiento" ? "disponible" : "mantenimiento")}>{u.codigo.slice(-2)}</button>
                    ))}</dd>
                  </div>
                ))}
              </dl>
            </div>
          ))}
        </div>
      </section>
    </article>
  );
}

/* ------------------------------------------------------------------ Bandeja */
const EVENTO = { despacho: "Despacho", escalamiento: "Reemplazo", confirmado: "Brigada confirmada", alerta_coordinador: "Alerta al coordinador", cierre: "Cierre e informe" };

function Bandeja({ n8n }) {
  const [msgs] = useSondeo("/api/notificaciones");
  return (
    <article className="hoja">
      <CabezaHoja titulo="Notificaciones" copia="Original, coordinación HSE"
        bajada={n8n
          ? "Eventos que la aplicación publicó en n8n. n8n los convierte en correos y SMS; aquí queda la copia con cada enlace de confirmación."
          : "Modo simulación: estos son los eventos que se enviarían a n8n. Use los enlaces para responder como brigadista."} />
      {msgs?.length === 0 && <div className="vacio"><p><b>Aún no se ha publicado ningún evento.</b> Cada despacho, reemplazo, confirmación, alerta y cierre aparecerá aquí.</p></div>}
      <ol className="talonario">
        {msgs?.map((m, i) => (
          <li key={i} className="talon">
            <header>
              <Sello estado={m.evento === "alerta_coordinador" ? "vencido" : m.evento === "confirmado" ? "confirmado" : "reservado"} texto={EVENTO[m.evento] || m.evento} />
              <b className="folio-mini">{m.incidente?.codigo}</b>
              <span className="num tenue">{new Date(m.emitido_en).toLocaleTimeString("es-CO")}</span>
              <span className={`via ${m.canal === "n8n" ? "vivo" : ""}`}>{m.canal === "n8n" ? "Entregado a n8n" : m.canal || "simulación"}</span>
            </header>
            {m.motivo && <p className="talon-motivo"><Icono nombre="alerta" tam={15} />{m.motivo}</p>}
            {m.destinatarios?.length > 0 && (
              <>
                <table className="planilla compacta">
                  <thead><tr><th>Para</th><th>Rol</th><th>Celular</th><th>Correo</th><th><span className="solo-lector">Enlace</span></th></tr></thead>
                  <tbody>{m.destinatarios.map((d) => (
                    <tr key={d.url_confirmar}>
                      <td><b>{d.nombre}</b>{d.usuario && <span className="tenue num"> · {d.usuario}</span>}</td>
                      <td>{ROL[d.rol] || d.rol}</td>
                      <td className="num">{d.telefono}</td>
                      <td className="tenue">{d.email}</td>
                      <td><a className="boton mini sec" href={d.url_confirmar} target="_blank" rel="noopener noreferrer">Abrir enlace<Icono nombre="enlace" tam={14} /></a></td>
                    </tr>
                  ))}</tbody>
                </table>
                <p className="sms"><span>SMS</span>ARKOF {m.incidente.codigo} Nivel {m.incidente.nivel} en {m.incidente.municipio}. Confirma en {m.destinatarios[0].url_confirmar}</p>
              </>
            )}
            {m.error_n8n && <p className="tenue pequeno">n8n no respondió: {m.error_n8n}</p>}
          </li>
        ))}
      </ol>
    </article>
  );
}
