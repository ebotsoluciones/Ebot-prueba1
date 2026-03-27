from datetime import datetime, timedelta
from storage import cargar_json, guardar_json
from config import HORARIO_INICIO, HORARIO_FIN, INTERVALO, BLOQUEOS_FILE, TURNOS_FILE, MENSAJES_FILE


# ---------------- HORARIOS ----------------

def generar_horarios():
    horarios = []
    inicio = datetime.strptime(HORARIO_INICIO, "%H:%M")
    fin    = datetime.strptime(HORARIO_FIN,    "%H:%M")
    actual = inicio
    while actual <= fin:
        horarios.append(actual.strftime("%H:%M"))
        actual += timedelta(minutes=INTERVALO)
    return horarios


def normalizar_hora(hora_str):
    """Acepta '9:00' o '09:00' y devuelve siempre '09:00'."""
    try:
        return datetime.strptime(hora_str.strip(), "%H:%M").strftime("%H:%M")
    except ValueError:
        return None


# ---------------- BLOQUEOS ----------------

def horario_bloqueado(fecha, hora):
    bloqueos = cargar_json(BLOQUEOS_FILE)
    return any(b["fecha"] == fecha and b["hora"] == hora for b in bloqueos)


def bloquear_horario(fecha, hora):
    bloqueos = cargar_json(BLOQUEOS_FILE)
    if not any(b["fecha"] == fecha and b["hora"] == hora for b in bloqueos):
        bloqueos.append({"fecha": fecha, "hora": hora})
        guardar_json(BLOQUEOS_FILE, bloqueos)


# ---------------- TURNOS ----------------

def obtener_turnos():
    return cargar_json(TURNOS_FILE)


def guardar_turnos(data):
    guardar_json(TURNOS_FILE, data)


def turnos_usuario(numero):
    hoy = datetime.now().date()
    return [
        t for t in obtener_turnos()
        if t["telefono"] == numero
        and datetime.strptime(t["fecha"], "%d/%m/%Y").date() >= hoy
    ]


def horarios_libres(fecha_str):
    horarios = generar_horarios()
    turnos   = obtener_turnos()
    ocupados = [t["hora"] for t in turnos if t["fecha"] == fecha_str]
    return [
        h for h in horarios
        if h not in ocupados and not horario_bloqueado(fecha_str, h)
    ]


def agregar_turno(nombre, telefono, fecha_str, hora):
    turnos = obtener_turnos()
    turnos.append({
        "nombre":   nombre,
        "telefono": telefono,
        "fecha":    fecha_str,
        "hora":     hora
    })
    guardar_turnos(turnos)


def cancelar_turno(telefono, fecha_str, hora):
    turnos = obtener_turnos()
    nuevos = [
        t for t in turnos
        if not (t["telefono"] == telefono and t["fecha"] == fecha_str and t["hora"] == hora)
    ]
    guardar_turnos(nuevos)
    return len(nuevos) < len(turnos)   # True si se canceló algo


# ---------------- MENSAJES ----------------

def guardar_mensaje(nombre, numero, texto):
    mensajes = cargar_json(MENSAJES_FILE)
    mensajes.setdefault("data", [])
    mensajes["data"].append({
        "nombre":   nombre,
        "telefono": numero,
        "mensaje":  texto,
        "fecha":    datetime.now().isoformat(),
        "leido":    False
    })
    guardar_json(MENSAJES_FILE, mensajes)
