import { useEffect, useState } from "react";
import { api, cuandoSeCierreLaSesion, enviar } from "./api.js";
import Consola from "./Consola.jsx";
import Ingreso from "./Ingreso.jsx";
import Portal from "./Portal.jsx";

// Segmentación por rol: el coordinador opera la consola; el brigadista solo ve su portal.
export default function App() {
  const [usuario, setUsuario] = useState(undefined); // undefined = verificando sesión
  useEffect(() => {
    cuandoSeCierreLaSesion(() => setUsuario(null));
    api("/api/auth/yo").then(setUsuario).catch(() => setUsuario(null));
  }, []);
  const salir = () => enviar("/api/auth/salir").finally(() => setUsuario(null));

  if (usuario === undefined) return <p className="cargando">Cargando…</p>;
  if (!usuario) return <Ingreso alIngresar={setUsuario} />;
  return usuario.rol === "coordinador"
    ? <Consola usuario={usuario} alSalir={salir} />
    : <Portal usuario={usuario} alSalir={salir} />;
}
