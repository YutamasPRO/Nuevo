import os
from collections import deque

import configcatclient
from flask import Flask, jsonify, render_template_string, request


class Calcular:
    @staticmethod
    def sum(a: int, b: int) -> int:
        return a + b


app = Flask(__name__)

# Últimas 5 operaciones realizadas (en memoria)
HISTORIAL = deque(maxlen=5)

_cliente_configcat = None

PAGINA_TEMA = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ConfigCat Feature Toggle</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #f8f9fc; color: #111827;
           display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    body.oscuro { background: #111827; color: #f9fafb; }
    .tarjeta { background: #ffffff; color: #111827; border-radius: 24px; padding: 40px;
               max-width: 420px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,.12); }
    code { background: #eef2ff; color: #3730a3; padding: 2px 6px; border-radius: 6px; }
    .estado { display: flex; justify-content: space-between; align-items: center; text-align: left;
              background: #f3f4f6; border-radius: 16px; padding: 16px; margin: 24px 0; }
    .etiqueta { padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: 14px; }
    .inactivo { background: #fee2e2; color: #991b1b; }
    .activo { background: #dcfce7; color: #166534; }
    button { background: #4f46e5; color: white; border: 0; border-radius: 12px;
             padding: 12px 20px; font-size: 16px; cursor: pointer; }
    button:disabled { background: #9ca3af; cursor: not-allowed; }
    small { color: #6b7280; display: block; margin-top: 16px; font-style: italic; }
  </style>
</head>
<body>
  <div class="tarjeta">
    <h1>ConfigCat Feature Toggle</h1>
    <p>Evaluación del flag booleano <code>dark_mode_enabled</code>.</p>
    <div class="estado">
      <div>
        <small style="margin:0;font-style:normal">ESTADO DEL FLAG</small>
        <span id="texto">dark_mode_enabled = {{ 'true (Habilitado)' if activo else 'false (Deshabilitado)' }}</span>
      </div>
      <span id="etiqueta" class="etiqueta {{ 'activo' if activo else 'inactivo' }}">
        {{ 'Activo' if activo else 'Inactivo' }}
      </span>
    </div>
    <button id="boton" {{ '' if activo else 'disabled' }}>Cambiar tema claro / oscuro</button>
    <small id="nota">
      {{ 'El botón de alternar tema está habilitado por Feature Toggle.'
         if activo else 'El botón de alternar tema se encuentra deshabilitado por Feature Toggle.' }}
    </small>
  </div>
  <script>
    const boton = document.getElementById("boton");
    boton.addEventListener("click", () => document.body.classList.toggle("oscuro"));
    async function actualizar() {
      const r = await fetch("/estado-tema");
      const d = await r.json();
      const activo = d.dark_mode_enabled;
      boton.disabled = !activo;
      document.getElementById("etiqueta").textContent = activo ? "Activo" : "Inactivo";
      document.getElementById("etiqueta").className = "etiqueta " + (activo ? "activo" : "inactivo");
      document.getElementById("texto").textContent =
        "dark_mode_enabled = " + (activo ? "true (Habilitado)" : "false (Deshabilitado)");
      document.getElementById("nota").textContent = activo
        ? "El botón de alternar tema está habilitado por Feature Toggle."
        : "El botón de alternar tema se encuentra deshabilitado por Feature Toggle.";
      if (!activo) document.body.classList.remove("oscuro");
    }
    setInterval(actualizar, 5000);
  </script>
</body>
</html>"""


def leer_flag(clave: str) -> bool:
    """Lee un feature toggle booleano desde ConfigCat. Si no hay SDK key, queda en OFF."""
    global _cliente_configcat
    sdk_key = os.environ.get("CONFIGCAT_SDK_KEY")
    if not sdk_key:
        return False
    if _cliente_configcat is None:
        _cliente_configcat = configcatclient.get(sdk_key)
    return bool(_cliente_configcat.get_value(clave, False))


def historial_activo() -> bool:
    return leer_flag("historial")


def dark_mode_activo() -> bool:
    return leer_flag("dark_mode_enabled")


@app.get("/")
def inicio():
    return render_template_string(PAGINA_TEMA, activo=dark_mode_activo())


@app.get("/estado-tema")
def estado_tema():
    return jsonify(dark_mode_enabled=dark_mode_activo())


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/sumar")
def sumar():
    try:
        a = int(request.args["a"])
        b = int(request.args["b"])
    except (KeyError, ValueError):
        return jsonify(error="Los parámetros a y b deben ser números enteros"), 400
    resultado = Calcular.sum(a, b)
    HISTORIAL.append({"operacion": "sumar", "a": a, "b": b, "resultado": resultado})
    return jsonify(resultado=resultado)


@app.get("/historial")
def historial():
    if not historial_activo():
        return jsonify(error="Funcionalidad no disponible"), 404
    return jsonify(historial=list(HISTORIAL))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
