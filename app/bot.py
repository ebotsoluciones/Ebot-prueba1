import json
import os
from datetime import datetime, timedelta

# ---------------- CONFIG ----------------

TURNOS_FILE = "data/turnos.json"
MENSAJES_FILE = "data/mensajes.json"
BLOQUEOS_FILE = "data/bloqueos.json"
ESTADO_FILE = "data/estado.json"

ADMINS = ["whatsapp:+5493515645624"]

HORARIO_INICIO = "09:00"
HORARIO_FIN = "19:00"
INTERVALO = 30

# ---------------- STORAGE ----------------

def cargar_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------- ESTADO ----------------

def get_estado():
    return cargar_json(ESTADO_FILE)

def save_estado(data):
    guardar_json(ESTADO_FILE, data)

def set_user_state(numero, key, value):
    estado = get_estado()
    estado.setdefault(numero, {})
    estado[numero][key] = value
    save_estado(estado)

def get_user_state(numero, key, default=None):
    estado = get_estado()
    return estado.get(numero, {}).get(key, default)

def clear_user(numero):
    estado = get_estado()
    estado[numero] = {}
    save_estado(estado)

# ---------------- HORARIOS ----------------

def generar_horarios():
    horarios = []
    inicio = datetime.strptime(HORARIO_INICIO, "%H:%M")
    fin = datetime.strptime(HORARIO_FIN, "%H:%M")
    actual = inicio
    while actual <= fin:
        horarios.append(actual.strftime("%H:%M"))
        actual += timedelta(minutes=INTERVALO)
    return horarios

# ---------------- BLOQUEOS ----------------

def horario_bloqueado(fecha, hora):
    bloqueos = cargar_json(BLOQUEOS_FILE)
    return any(b["fecha"] == fecha and b["hora"] == hora for b in bloqueos)

# ---------------- TURNOS ----------------

def obtener_turnos():
    return cargar_json(TURNOS_FILE)

def guardar_turnos(data):
    guardar_json(TURNOS_FILE, data)

def turnos_usuario(numero):
    return [t for t in obtener_turnos() if t["telefono"] == numero]

# ---------------- MENSAJES ----------------

def guardar_mensaje(nombre, numero, texto):
    mensajes = cargar_json(MENSAJES_FILE)
    mensajes.append({
        "nombre": nombre,
        "telefono": numero,
        "mensaje": texto,
        "fecha": datetime.now().isoformat(),
        "leido": False
    })
    guardar_json(MENSAJES_FILE, mensajes)

# ---------------- MENUS ----------------

MENU_PACIENTE = """
🦙 E-Bot

1 Turno
2 Mis turnos
3 Mensaje
4 Urgencia
5 Informes
6 Salir
"""

MENU_ADMIN = """
🛠 ADMIN

1 Turnos hoy
2 Próximos
3 Mensajes
4 Nuevo turno
5 Cancelar turno
6 Bloquear agenda
7 Salir
"""

# ---------------- CORE ----------------

def procesar(numero, body, resp):

    texto = body.lower()
    msg = resp.message()

    estado = get_user_state(numero, "estado", "MENU")

    if texto in ["menu", "/start"]:
        set_user_state(numero, "estado", "MENU")
        msg.body(MENU_ADMIN if numero in ADMINS else MENU_PACIENTE)
        return

    if texto in ["admin", "adm"]:
        if numero in ADMINS:
            set_user_state(numero, "estado", "ADMIN")
            msg.body(MENU_ADMIN)
        else:
            msg.body("No autorizado")
        return

    if estado == "ADMIN":
        manejar_admin(numero, body, msg)
        return

    if estado == "MENU":
        manejar_menu(numero, body, msg)
        return

    if estado == "TURNO_NOMBRE":
        set_user_state(numero, "nombre", body)
        set_user_state(numero, "estado", "TURNO_FECHA")
        msg.body("Ingrese fecha (dd/mm/yyyy)")
        return

    if estado == "TURNO_FECHA":
        try:
            fecha = datetime.strptime(body, "%d/%m/%Y").date()
        except:
            msg.body("Formato inválido")
            return

        if fecha < datetime.now().date():
            msg.body("Fecha pasada")
            return

        set_user_state(numero, "fecha", body)
        set_user_state(numero, "estado", "TURNO_HORA")

        horarios = generar_horarios()
        turnos = obtener_turnos()
        ocupados = [t["hora"] for t in turnos if t["fecha"] == body]

        libres = [
            h for h in horarios
            if h not in ocupados and not horario_bloqueado(body, h)
        ]

        if not libres:
            msg.body("Sin horarios disponibles")
            set_user_state(numero, "estado", "MENU")
            return

        msg.body("Horarios:\n" + "\n".join(libres))
        return

    if estado == "TURNO_HORA":
        hora = body.strip()
        fecha = get_user_state(numero, "fecha")

        if horario_bloqueado(fecha, hora):
            msg.body("Horario bloqueado")
            return

        turnos = obtener_turnos()

        if any(t["fecha"] == fecha and t["hora"] == hora for t in turnos):
            msg.body("Ocupado")
            return

        turnos.append({
            "nombre": get_user_state(numero, "nombre"),
            "telefono": numero,
            "fecha": fecha,
            "hora": hora
        })

        guardar_turnos(turnos)

        msg.body(f"✅ Turno confirmado\n{fecha} {hora}")

        clear_user(numero)
        return

# ---------------- MENU ----------------

def manejar_menu(numero, body, msg):

    if body == "1":
        set_user_state(numero, "estado", "TURNO_NOMBRE")
        msg.body("Nombre y apellido")
        return

    if body == "2":
        lista = turnos_usuario(numero)
        if not lista:
            msg.body("Sin turnos")
        else:
            salida = "\n".join([f"{t['fecha']} {t['hora']}" for t in lista])
            msg.body(salida)
        return

    if body == "3":
        set_user_state(numero, "estado", "MENSAJE")
        msg.body("Escriba mensaje")
        return

    if body == "4":
        msg.body("Urgencias: +549000000000")
        return

    if body == "5":
        msg.body("Horario 09 a 19")
        return

    msg.body(MENU_PACIENTE)

# ---------------- ADMIN ----------------

def manejar_admin(numero, body, msg):

    turnos = obtener_turnos()

    if body == "1":
        hoy = datetime.now().strftime("%d/%m/%Y")
        lista = [t for t in turnos if t["fecha"] == hoy]
        msg.body("Sin turnos" if not lista else "\n".join(
            [f"{t['hora']} {t['nombre']}" for t in lista]
        ))
        return

    if body == "2":
        futuros = [t for t in turnos if datetime.strptime(t["fecha"], "%d/%m/%Y").date() >= datetime.now().date()]
        msg.body("Sin futuros" if not futuros else "\n".join(
            [f"{t['fecha']} {t['hora']} {t['nombre']}" for t in futuros]
        ))
        return

    if body == "3":
        mensajes = cargar_json(MENSAJES_FILE)
        msg.body("Sin mensajes" if not mensajes else "\n".join(
            [f"{m['nombre']}: {m['mensaje']}" for m in mensajes]
        ))
        return

    if body == "6":
        set_user_state(numero, "estado", "BLOQUEAR_FECHA")
        msg.body("Fecha a bloquear (dd/mm/yyyy)")
        return

    if body == "7":
        clear_user(numero)
        msg.body("Salida admin")
        return

    msg.body(MENU_ADMIN)
