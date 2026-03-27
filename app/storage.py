import json
import os

# Los archivos de turnos y bloqueos son LISTAS []
# El resto (estado, mensajes) son DICTS {}

_LIST_FILES = ("turnos", "bloqueos")


def _default(path):
    return [] if any(k in path for k in _LIST_FILES) else {}


def cargar_json(path):
    if not os.path.exists(path):
        return _default(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return _default(path)


def guardar_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
