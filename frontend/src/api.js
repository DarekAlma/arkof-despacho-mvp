// Cliente HTTP de la API. La sesión viaja en una cookie (mismo origen), así que no hay tokens en el front.
let alPerderSesion = () => {};
export const cuandoSeCierreLaSesion = (fn) => { alPerderSesion = fn; };

export async function api(ruta, opciones = {}) {
  const r = await fetch(ruta, { headers: { "Content-Type": "application/json" }, ...opciones });
  const datos = await r.json().catch(() => ({}));
  if (r.status === 401 && !ruta.startsWith("/api/auth/")) alPerderSesion();
  if (!r.ok) {
    const error = new Error(datos.error || `Error ${r.status}`);
    error.status = r.status;
    throw error;
  }
  return datos;
}

export const enviar = (ruta, cuerpo, metodo = "POST") =>
  api(ruta, { method: metodo, body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo) });
