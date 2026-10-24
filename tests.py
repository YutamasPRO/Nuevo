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


def test_historial_apagado_no_esta_disponible(monkeypatch):
    module = importlib.import_module("main")
    monkeypatch.setattr(module, "historial_activo", lambda: False)

    response = module.app.test_client().get("/historial")

    assert response.status_code == 404


def test_historial_encendido_muestra_operaciones(monkeypatch):
    module = importlib.import_module("main")
    module.HISTORIAL.clear()
    monkeypatch.setattr(module, "historial_activo", lambda: True)
    client = module.app.test_client()

    client.get("/sumar?a=2&b=3")
    response = client.get("/historial")

    assert response.status_code == 200
    assert response.get_json() == {
        "historial": [{"operacion": "sumar", "a": 2, "b": 3, "resultado": 5}]
    }


def test_historial_sin_sdk_key_queda_apagado(monkeypatch):
    module = importlib.import_module("main")
    monkeypatch.delenv("CONFIGCAT_SDK_KEY", raising=False)

    assert module.historial_activo() is False


def test_pagina_inicio_con_toggle_apagado(monkeypatch):
    module = importlib.import_module("main")
    monkeypatch.setattr(module, "dark_mode_activo", lambda: False)

    response = module.app.test_client().get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'class="etiqueta inactivo"' in html
    assert '<button id="boton" disabled>' in html


def test_pagina_inicio_con_toggle_encendido(monkeypatch):
    module = importlib.import_module("main")
    monkeypatch.setattr(module, "dark_mode_activo", lambda: True)

    response = module.app.test_client().get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'class="etiqueta activo"' in html
    assert '<button id="boton" >' in html


def test_estado_tema_refleja_el_flag(monkeypatch):
    module = importlib.import_module("main")
    monkeypatch.setattr(module, "dark_mode_activo", lambda: True)

    response = module.app.test_client().get("/estado-tema")

    assert response.get_json() == {"dark_mode_enabled": True}
