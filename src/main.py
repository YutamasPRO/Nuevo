import os
from collections import deque

import configcatclient
from flask import Flask, jsonify, request


class Calcular:
    @staticmethod
    def sum(a: int, b: int) -> int:
        return a + b


app = Flask(__name__)

# Últimas 5 operaciones realizadas (en memoria)
HISTORIAL = deque(maxlen=5)

_cliente_configcat = None


def historial_activo() -> bool:
    """Lee el feature toggle 'historial' desde ConfigCat. Si no hay SDK key, queda en OFF."""
    global _cliente_configcat
    sdk_key = os.environ.get("CONFIGCAT_SDK_KEY")
    if not sdk_key:
        return False
    if _cliente_configcat is None:
        _cliente_configcat = configcatclient.get(sdk_key)
    return bool(_cliente_configcat.get_value("historial", False))


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
