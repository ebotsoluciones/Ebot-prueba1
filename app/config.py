import os

# ---------------- ARCHIVOS ----------------

TURNOS_FILE   = "data/turnos.json"
MENSAJES_FILE = "data/mensajes.json"
BLOQUEOS_FILE = "data/bloqueos.json"
ESTADO_FILE   = "data/estado.json"

# ---------------- ADMINS ----------------

ADMINS = ["whatsapp:+5493515645624"]

# ---------------- MODO TEST ----------------
# En MODO_TEST cualquiera puede escribir "adm" para entrar al panel admin.
# En producción solo los números de ADMINS acceden.

MODO_TEST = True

# ---------------- HORARIOS ----------------

HORARIO_INICIO = "09:00"
HORARIO_FIN    = "19:00"
INTERVALO      = 30          # minutos entre turnos
