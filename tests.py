import importlib
import sys
from pathlib import Path

# Agregar directorio src al PATH para importar los módulos correctamente
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_index_module_imports():
    module = importlib.import_module("main")

    assert module is not None


def test_calcular_sum():
    from main import Calcular

    assert Calcular.sum(2, 3) == 5


def _client():
    module = importlib.import_module("main")
    return module.app.test_client()


def test_health_ok():
    response = _client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_sumar_ok():
    response = _client().get("/sumar?a=2&b=3")

    assert response.status_code == 200
    assert response.get_json() == {"resultado": 5}


def test_sumar_parametros_invalidos():
    response = _client().get("/sumar?a=x&b=3")

    assert response.status_code == 400
