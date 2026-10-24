import os

from flask import Flask, jsonify, request


class Calcular:
    @staticmethod
    def sum(a: int, b: int) -> int:
        return a + b


app = Flask(__name__)


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
    return jsonify(resultado=Calcular.sum(a, b))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
