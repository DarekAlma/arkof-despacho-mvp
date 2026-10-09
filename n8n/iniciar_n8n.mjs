// Arranca n8n local para el MVP con las variables de backend/.env (un solo lugar para configurar todo).
//
//   node n8n/iniciar_n8n.mjs            -> inicia n8n en http://localhost:5678
//   node n8n/iniciar_n8n.mjs importar   -> importa (o actualiza) el flujo n8n/arkof_despacho_workflow.json
//   node n8n/iniciar_n8n.mjs activar    -> deja el flujo activo (URL de producción del webhook)
//
// Variables que n8n toma de backend/.env:
//   N8N_SHARED_SECRET        secreto que n8n envía en X-ARKOF-Token al verificar el plazo (el mismo que usa Flask)
//   TWILIO_FROM_NUMBER       número remitente de Twilio (+1…); si falta, el nodo usa el número mágico de prueba
//   ARKOF_CORREO_REMITENTE   dirección que aparece en "From" de los correos; con Gmail debe ser su propia cuenta
// Los datos de n8n (credenciales cifradas, historial) quedan en N8N_USER_FOLDER, por defecto ~/.arkof-n8n,
// fuera del repositorio.
import { spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const ID_FLUJO = "arkofDespacho001";

function leerEnv(ruta) {
  if (!existsSync(ruta)) return {};
  const vars = {};
  for (const linea of readFileSync(ruta, "utf8").split(/\r?\n/)) {
    const m = linea.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (m) vars[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
  return vars;
}

const env = leerEnv(join(raiz, "backend", ".env"));
const entorno = {
  ...process.env,
  N8N_USER_FOLDER: process.env.N8N_USER_FOLDER || join(homedir(), ".arkof-n8n"),
  N8N_BLOCK_ENV_ACCESS_IN_NODE: "false", // los nodos leen $env.N8N_SHARED_SECRET, etc.
  GENERIC_TIMEZONE: "America/Bogota",
  N8N_DIAGNOSTICS_ENABLED: "false",
  N8N_PERSONALIZATION_ENABLED: "false",
};
for (const clave of ["N8N_SHARED_SECRET", "TWILIO_FROM_NUMBER", "ARKOF_CORREO_REMITENTE"]) {
  if (env[clave] && !process.env[clave]) entorno[clave] = env[clave];
}

const orden = process.argv[2] || "iniciar";
const argumentos = {
  iniciar: ["start"],
  importar: ["import:workflow", `--input=${process.argv[3] || join(raiz, "n8n", "arkof_despacho_workflow.json")}`],
  activar: ["update:workflow", `--id=${ID_FLUJO}`, "--active=true"],
}[orden];
if (!argumentos) {
  console.error(`Orden desconocida "${orden}". Use: iniciar | importar | activar`);
  process.exit(1);
}

const faltan = ["N8N_SHARED_SECRET", "TWILIO_FROM_NUMBER", "ARKOF_CORREO_REMITENTE"].filter((c) => !entorno[c]);
if (orden === "iniciar" && faltan.length) console.warn(`Aviso: faltan en backend/.env: ${faltan.join(", ")}`);

const hijo = spawn("npx", ["--yes", "n8n@1", ...argumentos], { env: entorno, stdio: "inherit", shell: true });
hijo.on("exit", (codigo) => process.exit(codigo ?? 0));
