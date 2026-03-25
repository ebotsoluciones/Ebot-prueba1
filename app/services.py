from datetime import datetime, timedelta
from .storage import cargar_json
from .config import *

def generar_horarios():
    horarios = []
    inicio = datetime.strptime(HORARIO_INICIO, "%H:%M")
    fin = datetime.strptime(HORARIO_FIN, "%H:%M")
    actual = inicio
    while actual <= fin:
        horarios.append(actual.strftime("%H:%M"))
        actual += timedelta(minutes=INTERVALO)
    return horarios

def horario_bloqueado(fecha, hora):
    bloqueos = cargar_json(BLOQUEOS_FILE)
    return any(b["fecha"] == fecha and b["hora"] == hora for b in bloqueos)
