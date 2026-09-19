import importlib
import sys
from pathlib import Path

# Agregar directorio src al PATH para importar los módulos correctamente
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_index_module_imports():
    module = importlib.import_module("index")

    assert module is not None
