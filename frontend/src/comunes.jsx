import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";

// Hook de sondeo: las vistas se actualizan solas (la app no usa websockets).
export function useSondeo(ruta, intervalo = 3000) {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);
  const cargar = useCallback(
    () => api(ruta).then((d) => { setDatos(d); setError(null); }).catch((e) => setError(e.message)),
    [ruta],
  );
  useEffect(() => {
    cargar();
    const id = setInterval(cargar, intervalo);
    return () => clearInterval(id);
  }, [cargar, intervalo]);
  return [datos, cargar, error];
}

// Reloj compartido para las cuentas regresivas del plazo de confirmación (RN-07).
export function useAhora(paso = 1000) {
  const [ahora, setAhora] = useState(Date.now());
  useEffect(() => { const t = setInterval(() => setAhora(Date.now()), paso); return () => clearInterval(t); }, [paso]);
  return ahora;
}

export const TIPOS = { DERRAME_HIDROCARBURO: "Derrame de hidrocarburo", SUSTANCIA_NOCIVA: "Sustancia nociva", FUGA_GAS: "Fuga de gas" };
export const CICLO = ["reportado", "notificado", "confirmado", "en_ruta", "en_sitio", "controlado", "cerrado"];
export const ETIQUETA = {
  reportado: "Reportado", notificado: "Brigada notificada", confirmado: "Brigada confirmada",
  en_ruta: "En ruta", en_sitio: "En sitio", controlado: "Controlado", cerrado: "Cerrado",
};
export const ESTADO_ASIGNACION = {
  pendiente: "Pendiente", confirmado: "Confirmado", rechazado: "Rechazado", vencido: "Vencido", no_requerido: "No requerido",
};
export const ESTADO_RECURSO = {
  disponible: "Disponible", asignado: "Asignado", fuera_turno: "Fuera de turno", incapacitado: "Incapacitado",
  reservado: "Reservado", mantenimiento: "Mantenimiento",
};
export const ROL = { lider: "líder", tecnico: "técnico" };
export const CERT = { ANTIDERRAME: "Antiderrames", HAZMAT: "HAZMAT", PRIMEROS_AUXILIOS: "Primeros auxilios" };
export const EQUIPO = {
  KIT_ANTIDERRAME: "Kit antiderrames", BARRERA: "Barrera de contención", ABSORBENTE: "Paca absorbente",
  KIT_HAZMAT: "Kit HAZMAT", EPP: "Juego de EPP", VEHICULO: "Camioneta 4x4",
};
export const CANAL = { portal: "Portal del cliente", telefono: "Llamada telefónica", coordinador: "Coordinador" };

export const hora = (iso) => (iso ? new Date(iso).toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "—");
export const fechaHora = (iso) => (iso ? new Date(iso).toLocaleString("es-CO", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "—");
export const num = (n, d = 1) => (n == null ? "—" : n.toLocaleString("es-CO", { minimumFractionDigits: d, maximumFractionDigits: d }));
export const dur = (s) => (s == null ? "—" : s < 1 ? `${Math.round(s * 1000)} ms` : s < 60 ? `${num(s)} s` : `${num(s / 60)} min`);

// Segundos que faltan para que venza el plazo; negativo si ya venció.
export const restante = (venceEn, ahora) => (venceEn ? (new Date(venceEn).getTime() - ahora) / 1000 : null);
export const reloj = (s) => {
  const t = Math.max(0, Math.ceil(s));
  return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`;
};

// Iconos dibujados en un solo trazo (1.75) para toda la app.
const TRAZOS = {
  check: "M4 12.5l5 5L20 6.5",
  x: "M6 6l12 12M18 6L6 18",
  reloj: "M12 7v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z",
  pin: "M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11zM12 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z",
  telefono: "M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z",
  salir: "M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 16l-4-4 4-4M6 12h10",
  alerta: "M12 4l9 16H3l9-16zM12 10v4M12 17.2v.1",
  enlace: "M14 4h6v6M20 4l-9 9M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4",
  flecha: "M15 18l-6-6 6-6",
  reiniciar: "M4 12a8 8 0 1 0 2.4-5.7M4 4v5h5",
  documento: "M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6",
};
export function Icono({ nombre, tam = 18, className = "" }) {
  return (
    <svg className={`icono ${className}`} width={tam} height={tam} viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={TRAZOS[nombre]} />
    </svg>
  );
}

// Sello de goma: el estado siempre se lee como texto, el color solo refuerza.
export function Sello({ estado, texto, grande = false }) {
  const etiqueta = texto || ESTADO_ASIGNACION[estado] || ETIQUETA[estado] || ESTADO_RECURSO[estado] || estado;
  return <span className={`sello s-${estado}${grande ? " grande" : ""}`}>{etiqueta}</span>;
}

// Marca de nivel: la escala y la tinta crecen con la severidad (no solo el color).
export function Nivel({ n, conTexto = false }) {
  if (!n) return null;
  return (
    <span className={`nivel n${n}`} title={`Nivel ${n}`}>
      {conTexto && <span className="nivel-rotulo">Nivel</span>}
      <b>{n}</b>
    </span>
  );
}

// Casilla de formulario: número, rótulo y valor.
export function Casilla({ n, rotulo, children, className = "" }) {
  return (
    <div className={`casilla ${className}`}>
      <div className="casilla-rotulo">{n != null && <span className="casilla-n">{n}</span>}{rotulo}</div>
      <div className="casilla-valor">{children}</div>
    </div>
  );
}

// Encabezado de hoja: título a la izquierda, folio en tinta de serie a la derecha.
export function CabezaHoja({ titulo, bajada, copia, folio, children }) {
  return (
    <header className="hoja-cabeza">
      <div className="hoja-titulo">
        <h1>{titulo}</h1>
        {bajada && <p className="bajada">{bajada}</p>}
      </div>
      <div className="hoja-folio">
        <dl className="membrete">
          <div><dt>Empresa</dt><dd>ARKOF S.A.S.</dd></div>
          <div><dt>Proceso</dt><dd>Despacho de brigadas</dd></div>
          {copia && <div><dt>Copia</dt><dd>{copia}</dd></div>}
        </dl>
        {folio && <p className="folio"><span>N.º</span>{folio}</p>}
        {children}
      </div>
    </header>
  );
}

// Extrae las reglas citadas en la bitácora, p. ej. "(RN-02/03/04)", para trazar cada acción a su regla.
export function reglasCitadas(texto) {
  const m = texto.match(/\((RN-[^)]+)\)\.?$/);
  return m ? { limpio: texto.replace(m[0], "").trim().replace(/[;,]$/, ""), reglas: m[1] } : { limpio: texto, reglas: null };
}
