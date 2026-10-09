import { useState } from "react";
import { enviar } from "./api.js";
import {
  CERT, ESTADO_ASIGNACION, ETIQUETA, Icono, Nivel, ROL, Sello, TIPOS, fechaHora, num, reloj, restante, useAhora, useSondeo,
} from "./comunes.jsx";

// Portal del brigadista: la "copia amarilla" del formato. Pensado para el celular, en campo y con sol.
export default function Portal({ usuario, alSalir }) {
  const [datos, recargar] = useSondeo("/api/mi/asignaciones", 4000);
  const ahora = useAhora();
  const b = datos?.brigadista || usuario.brigadista;
  const lista = datos?.asignaciones || [];
  const pendientes = lista.filter((a) => a.estado === "pendiente");
  const enCurso = lista.filter((a) => a.estado === "confirmado" && a.incidente.estado !== "cerrado");
  const historial = lista.filter((a) => !pendientes.includes(a) && !enCurso.includes(a));

  return (
    <div className="portal">
      <header className="portal-cabeza">
        <div>
          <p className="marca">ARKOF</p>
          <p className="copia">Copia del brigadista</p>
        </div>
        <button className="salir" onClick={alSalir}><Icono nombre="salir" />Salir</button>
      </header>

      <section className="hoja amarilla ficha" aria-label="Mis datos">
        <div className="ficha-nombre">
          <h1>{b.nombre}</h1>
          <p>{ROL[b.rol]} · base {b.base}</p>
        </div>
        <Sello estado={b.estado} />
        <p className="certs">{b.certificaciones.map((c) => <span key={c} className="cert">{CERT[c] || c}</span>)}</p>
      </section>

      {datos && pendientes.length === 0 && enCurso.length === 0 && (
        <section className="hoja amarilla vacio">
          <p><b>No tiene convocatorias pendientes.</b></p>
          <p>Cuando el sistema lo asigne a un incidente le llegará un SMS y un correo, y la convocatoria aparecerá aquí para responder con un toque.</p>
        </section>
      )}

      {pendientes.map((a) => <Convocatoria key={a.id} a={a} ahora={ahora} alResponder={recargar} />)}
      {enCurso.map((a) => <DespachoEnCurso key={a.id} a={a} />)}

      {historial.length > 0 && (
        <section className="hoja amarilla historial" aria-labelledby="p-historial">
          <h2 className="banda" id="p-historial">Mis asignaciones anteriores</h2>
          <ul>
            {historial.map((a) => (
              <li key={a.id}>
                <div><b className="folio-mini">{a.incidente.codigo}</b><span>{TIPOS[a.incidente.tipo]} · {a.incidente.municipio}</span></div>
                <Sello estado={a.estado} />
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function Convocatoria({ a, ahora, alResponder }) {
  const [enviando, setEnviando] = useState(null);
  const [error, setError] = useState(null);
  const inc = a.incidente;
  const s = restante(a.vence_en, ahora);
  const responder = async (acepta) => {
    setEnviando(acepta ? "si" : "no"); setError(null);
    try { await enviar(`/api/mi/asignaciones/${a.id}/responder`, { acepta }); alResponder(); }
    catch (e) { setError(e.message); alResponder(); }
    finally { setEnviando(null); }
  };

  return (
    <section className="hoja amarilla convocatoria" aria-labelledby={`c-${a.id}`}>
      <h2 className="banda alerta" id={`c-${a.id}`}>Convocatoria: responda ahora</h2>
      <div className="conv-cabeza">
        <Nivel n={inc.nivel} conTexto />
        <div>
          <p className="folio"><span>N.º</span>{inc.codigo}</p>
          <p className="conv-tipo">{TIPOS[inc.tipo]}</p>
        </div>
      </div>
      <dl className="conv-datos">
        <div><dt>Su rol</dt><dd>{ROL[a.rol_en_brigada]}</dd></div>
        <div><dt>Lugar</dt><dd>{inc.municipio} · {num(a.distancia_km, 0)} km de su base</dd></div>
        <div><dt>Cliente</dt><dd>{inc.empresa}</dd></div>
        {inc.descripcion && <div><dt>Reporte</dt><dd>{inc.descripcion}</dd></div>}
      </dl>
      <div className={`plazo${s != null && s <= 60 ? " urge" : ""}`} role="timer" aria-live="off">
        <Icono nombre="reloj" tam={22} />
        {s > 0
          ? <p><b className="num">{reloj(s)}</b><span>para confirmar (plazo de {num(inc.sla_minutos, 0)} min)</span></p>
          : <p><b>El plazo venció</b><span>Si aún puede ir, confirme ya: el sistema está buscando reemplazo.</span></p>}
      </div>
      {error && <p className="error" role="alert"><Icono nombre="alerta" />{error}</p>}
      <div className="respuestas">
        <button className="boton grande si" disabled={!!enviando} onClick={() => responder(true)}>
          <Icono nombre="check" tam={22} />{enviando === "si" ? "Registrando…" : "Confirmo, voy en camino"}
        </button>
        <button className="boton grande no" disabled={!!enviando} onClick={() => responder(false)}>
          <Icono nombre="x" tam={22} />{enviando === "no" ? "Registrando…" : "No estoy disponible"}
        </button>
      </div>
    </section>
  );
}

function DespachoEnCurso({ a }) {
  const inc = a.incidente;
  const mapa = `https://www.google.com/maps?q=${inc.lat},${inc.lon}`;
  return (
    <section className="hoja amarilla en-curso" aria-labelledby={`e-${a.id}`}>
      <h2 className="banda verde" id={`e-${a.id}`}>Despacho en curso</h2>
      <div className="conv-cabeza">
        <Nivel n={inc.nivel} conTexto />
        <div>
          <p className="folio"><span>N.º</span>{inc.codigo}</p>
          <p className="conv-tipo">{TIPOS[inc.tipo]}</p>
        </div>
        <Sello key={inc.estado} estado={inc.estado} texto={ETIQUETA[inc.estado]} grande />
      </div>
      <dl className="conv-datos">
        <div><dt>Su respuesta</dt><dd>{ESTADO_ASIGNACION[a.estado]} · {fechaHora(a.respondido_en)}</dd></div>
        <div><dt>Lugar</dt><dd>{inc.municipio} · {inc.lat.toFixed(4)}, {inc.lon.toFixed(4)}</dd></div>
        <div><dt>Cliente</dt><dd>{inc.empresa}</dd></div>
      </dl>
      <a className="boton sec ancho" href={mapa} target="_blank" rel="noopener noreferrer"><Icono nombre="pin" />Abrir la ubicación en el mapa</a>

      <h3>Brigada confirmada</h3>
      <ul className="companeros">
        {a.brigada.map((x) => (
          <li key={x.nombre}>
            <span><b>{x.nombre}{x.yo && " (usted)"}</b><span className="tenue">{ROL[x.rol_en_brigada]}</span></span>
            {!x.yo && <a href={`tel:${x.telefono}`} aria-label={`Llamar a ${x.nombre}`}><Icono nombre="telefono" />{x.telefono}</a>}
          </li>
        ))}
      </ul>
      <h3>Kit reservado</h3>
      <ul className="kit compacto">
        {a.equipos.map((e) => <li key={e.codigo}><b className="num">{e.codigo}</b><span>{e.descripcion}</span><span className="tenue">{e.base}</span></li>)}
      </ul>
      <p className="tenue pequeno">Los cambios de estado en campo (en ruta, en sitio, controlado) los registra el coordinador. Reporte los hitos por radio o teléfono.</p>
    </section>
  );
}
