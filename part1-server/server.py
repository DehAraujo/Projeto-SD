import zmq
import json
import os
from datetime import datetime

# Arquivos de persistência
USERS_FILE = "users.json"
CHANNELS_FILE = "channels.json"

# Garante arquivos de persistência
for f in [USERS_FILE, CHANNELS_FILE]:
    if not os.path.exists(f):
        with open(f, "w") as fp:
            json.dump([], fp)

def load_json(filename):
    with open(filename, "r") as fp:
        return json.load(fp)

def save_json(filename, data):
    with open(filename, "w") as fp:
        json.dump(data, fp, indent=2)

ctx = zmq.Context()
rep = ctx.socket(zmq.REP)
rep.bind("tcp://*:5556")

print("🧠 Servidor (Parte 1 - JSON) rodando em tcp://*:5556")

while True:
    raw = rep.recv()
    msg = json.loads(raw.decode("utf-8"))
    service = msg.get("service")
    data = msg.get("data", {})
    timestamp = datetime.now().isoformat()

    # Serviço: LOGIN -------------------------------------------------------
    if service == "login":
        user = data.get("user")
        users = load_json(USERS_FILE)
        if user in users:
            reply = {
                "service": "login",
                "data": {
                    "status": "erro",
                    "timestamp": timestamp,
                    "description": "Usuário já logado"
                }
            }
        else:
            users.append(user)
            save_json(USERS_FILE, users)
            reply = {
                "service": "login",
                "data": {
                    "status": "sucesso",
                    "timestamp": timestamp
                }
            }

    # Serviço: USERS -------------------------------------------------------
    elif service == "users":
        users = load_json(USERS_FILE)
        reply = {
            "service": "users",
            "data": {
                "timestamp": timestamp,
                "users": users
            }
        }

    # Serviço: CHANNEL -----------------------------------------------------
    elif service == "channel":
        channel = data.get("channel")
        channels = load_json(CHANNELS_FILE)
        if channel in channels:
            reply = {
                "service": "channel",
                "data": {
                    "status": "erro",
                    "timestamp": timestamp,
                    "description": "Canal já existe"
                }
            }
        else:
            channels.append(channel)
            save_json(CHANNELS_FILE, channels)
            reply = {
                "service": "channel",
                "data": {
                    "status": "sucesso",
                    "timestamp": timestamp
                }
            }

    # Serviço: CHANNELS ----------------------------------------------------
    elif service == "channels":
        channels = load_json(CHANNELS_FILE)
        reply = {
            "service": "channels",
            "data": {
                "timestamp": timestamp,
                "channels": channels
            }
        }

    # Serviço inválido -----------------------------------------------------
    else:
        reply = {
            "service": "erro",
            "data": {
                "timestamp": timestamp,
                "description": "Serviço inválido"
            }
        }

    rep.send_string(json.dumps(reply))
