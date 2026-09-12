import importlib


def test_index_module_imports():
    module = importlib.import_module("index")

    assert module is not None