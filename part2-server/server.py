import zmq
import json
import os
import time

DATA_PATH = "data"
USERS_FILE = os.path.join(DATA_PATH, "users.json")
CHANNELS_FILE = os.path.join(DATA_PATH, "channels.json")
MESSAGES_FILE = os.path.join(DATA_PATH, "messages.json")

os.makedirs(DATA_PATH, exist_ok=True)

for f in [USERS_FILE, CHANNELS_FILE, MESSAGES_FILE]:
    if not os.path.exists(f):
        with open(f, "w") as fp:
            json.dump([], fp)

def read_json(file):
    with open(file, "r") as fp:
        return json.load(fp)

def write_json(file, data):
    with open(file, "w") as fp:
        json.dump(data, fp, indent=2)

ctx = zmq.Context()

# REQ/REP socket
rep = ctx.socket(zmq.REP)
rep.bind("tcp://*:5555")

# PUB socket
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5556")

print("🧠 Servidor PUB/SUB rodando em 5555 (REQ/REP) e 5556 (PUB)")

while True:
    msg = rep.recv_json()
    service = msg["service"]
    data = msg["data"]

    timestamp = time.time()
    response = {"service": service, "data": {"timestamp": timestamp}}

    if service == "publish":
        user = data["user"]
        channel = data["channel"]
        message = data["message"]

        channels = read_json(CHANNELS_FILE)
        if channel not in channels:
            response["data"].update({"status": "erro", "message": "Canal não existe"})
        else:
            payload = {"user": user, "channel": channel, "message": message, "timestamp": timestamp}
            pub.send_string(f"{channel} {json.dumps(payload)}")

            messages = read_json(MESSAGES_FILE)
            messages.append(payload)
            write_json(MESSAGES_FILE, messages)

            response["data"].update({"status": "OK"})
        rep.send_json(response)

    elif service == "message":
        src = data["src"]
        dst = data["dst"]
        message = data["message"]

        users = read_json(USERS_FILE)
        if dst not in users:
            response["data"].update({"status": "erro", "message": "Usuário não existe"})
        else:
            payload = {"src": src, "dst": dst, "message": message, "timestamp": timestamp}
            pub.send_string(f"{dst} {json.dumps(payload)}")

            messages = read_json(MESSAGES_FILE)
            messages.append(payload)
            write_json(MESSAGES_FILE, messages)

            response["data"].update({"status": "OK"})
        rep.send_json(response)

    else:
        response["data"].update({"status": "erro", "message": "Serviço inválido"})
        rep.send_json(response)
