import { useState } from "react";
import { enviar } from "./api.js";
import { Icono } from "./comunes.jsx";

// Cuentas de la semilla (datos ficticios) para agilizar la demostración y la grabación del video.
const CUENTAS_DEMO = [
  { usuario: "coordinador", quien: "Coordinación HSE", rol: "Consola de despacho" },
  { usuario: "paola.diaz", quien: "Paola Díaz", rol: "Líder · Acacías" },
  { usuario: "andres.rojas", quien: "Andrés Rojas", rol: "Líder · Villavicencio" },
  { usuario: "karen.suarez", quien: "Karen Suárez", rol: "Técnica · Acacías" },
];

export default function Ingreso({ alIngresar }) {
  const [usuario, setUsuario] = useState("");
  const [clave, setClave] = useState("");
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);

  const ingresar = async (e) => {
    e.preventDefault();
    setError(null); setEnviando(true);
    try { alIngresar(await enviar("/api/auth/ingresar", { usuario, clave })); }
    catch (err) { setError(err.status === 401 ? "Usuario o contraseña incorrectos. Revise ambos campos e intente de nuevo." : err.message); }
    finally { setEnviando(false); }
  };

  return (
    <div className="ingreso">
      <section className="ingreso-tapa">
        <p className="marca">ARKOF</p>
        <p className="tapa-titulo">Despacho de brigadas ante contingencias ambientales</p>
        <p className="tapa-texto">
          El sistema clasifica el incidente, elige la brigada certificada más cercana, reserva el kit y notifica en paralelo.
          El coordinador solo atiende las excepciones.
        </p>
        <dl className="tapa-cifras">
          <div><dt>Antes</dt><dd>25 a 40 min</dd><dd className="tapa-nota">del reporte al despacho, por teléfono</dd></div>
          <div><dt>Con el sistema</dt><dd>6,4 min</dd><dd className="tapa-nota">hasta la brigada confirmada (simulación, sección 6.8)</dd></div>
        </dl>
        <p className="tapa-pie">MVP académico · Gerencia de Operaciones de TI · Universidad de La Sabana, 2026-2. Todos los datos son ficticios.</p>
      </section>

      <section className="ingreso-hoja" aria-labelledby="titulo-ingreso">
        <form className="hoja hoja-ingreso" onSubmit={ingresar}>
          <header className="hoja-cabeza compacta">
            <div className="hoja-titulo">
              <h1 id="titulo-ingreso">Ingreso</h1>
              <p className="bajada">El coordinador entra a la consola; cada brigadista, a sus convocatorias.</p>
            </div>
          </header>
          <div className="casillas una">
            <label className="casilla campo">
              <span className="casilla-rotulo"><span className="casilla-n">1</span>Usuario</span>
              <input value={usuario} onChange={(e) => setUsuario(e.target.value)} autoComplete="username" autoCapitalize="none"
                spellCheck={false} placeholder="nombre.apellido" required />
            </label>
            <label className="casilla campo">
              <span className="casilla-rotulo"><span className="casilla-n">2</span>Contraseña</span>
              <input type="password" value={clave} onChange={(e) => setClave(e.target.value)} autoComplete="current-password" required />
            </label>
          </div>
          {error && <p className="error" role="alert"><Icono nombre="alerta" />{error}</p>}
          <button className="boton ancho" disabled={enviando}>{enviando ? "Verificando…" : "Ingresar"}</button>

          <div className="demo-cuentas">
            <p>Cuentas de demostración (datos ficticios). Solicite la contraseña al equipo del proyecto.</p>
            <ul>
              {CUENTAS_DEMO.map((c) => (
                <li key={c.usuario}>
                  <button type="button" className="cuenta-demo" onClick={() => setUsuario(c.usuario)} aria-label={`Usar la cuenta ${c.usuario}`}>
                    <b>{c.usuario}</b><span>{c.quien} · {c.rol}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </form>
      </section>
    </div>
  );
}
