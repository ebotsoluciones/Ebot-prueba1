import os

# ---------------- RUTAS ----------------

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TURNOS_FILE   = os.path.join(BASE, "data", "turnos.json")
MENSAJES_FILE = os.path.join(BASE, "data", "mensajes.json")
BLOQUEOS_FILE = os.path.join(BASE, "data", "bloqueos.json")
ESTADO_FILE   = os.path.join(BASE, "data", "estado.json")

# ---------------- ADMINS ----------------

ADMINS = ["whatsapp:+5493515645624"]

# ---------------- MODO TEST ----------------

MODO_TEST = True

# ---------------- HORARIOS ----------------

HORARIO_INICIO = "09:00"
HORARIO_FIN    = "19:00"
INTERVALO      = 30
