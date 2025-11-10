import zmq
import msgpack
import json
import os
import time
from datetime import datetime
from clock import LogicalClock

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Estado em memória
users = load_data(USERS_FILE)
channels = load_data(CHANNELS_FILE)
messages = load_data(MESSAGES_FILE)

# --- Configuração ZMQ ---
context = zmq.Context()
rep_socket = context.socket(zmq.REP)
rep_socket.bind("tcp://*:5556")

pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://proxy:5557")

ref_socket = context.socket(zmq.REQ)
ref_socket.connect("tcp://ref:5555")

print("🧠 Servidor Parte 4 iniciado")

clock = LogicalClock()
server_name = os.environ.get("SERVER_NAME", "server")
rank = None
coordinator = None
message_counter = 0

# --- Requisição de rank ---
clock.tick()
rank_req = {
    "service": "rank",
    "data": {"user": server_name, "timestamp": datetime.now().isoformat(), "clock": clock.value}
}
ref_socket.send(msgpack.packb(rank_req, use_bin_type=True))
rank_resp = msgpack.unpackb(ref_socket.recv(), raw=False)
clock.update(rank_resp["data"]["clock"])
rank = rank_resp["data"]["rank"]
print(f"📊 {server_name} recebeu rank {rank}")

# --- Loop principal ---
while True:
    try:
        raw_msg = rep_socket.recv()
        msg = msgpack.unpackb(raw_msg, raw=False)
        clock.update(msg["data"].get("clock", 0))
    except Exception as e:
        print("Erro recebendo mensagem:", e)
        continue

    service = msg.get("service")
    data = msg.get("data", {})
    current_timestamp = datetime.now().isoformat()
    response = {"service": service, "data": {}}

    # LOGIN
    if service == "login":
        user = data.get("user")
        if user not in users:
            users.append(user)
            save_data(USERS_FILE, users)
        response["data"] = {"status": "sucesso", "timestamp": current_timestamp, "clock": clock.tick()}

    # USERS
    elif service == "users":
        response["data"] = {"users": users, "timestamp": current_timestamp, "clock": clock.tick()}

    # CHANNEL
    elif service == "channel":
        ch = data.get("channel")
        if ch not in channels:
            channels.append(ch)
            save_data(CHANNELS_FILE, channels)
        response["data"] = {"status": "sucesso", "timestamp": current_timestamp, "clock": clock.tick()}

    # PUBLISH
    elif service == "publish":
        user = data.get("user")
        channel = data.get("channel")
        message = data.get("message")
        if channel not in channels:
            response["data"] = {"status": "erro", "message": "Canal inexistente", "timestamp": current_timestamp, "clock": clock.tick()}
        else:
            pub_socket.send(msgpack.packb({
                "topic": channel, "user": user, "message": message,
                "timestamp": current_timestamp, "clock": clock.tick()
            }, use_bin_type=True))
            messages.append({"type": "channel", "from": user, "to": channel, "message": message, "timestamp": current_timestamp})
            save_data(MESSAGES_FILE, messages)
            response["data"] = {"status": "OK", "timestamp": current_timestamp, "clock": clock.value}

    # MESSAGE PRIVADA
    elif service == "message":
        src = data.get("src")
        dst = data.get("dst")
        message = data.get("message")
        if dst not in users:
            response["data"] = {"status": "erro", "message": "Usuário inexistente", "timestamp": current_timestamp, "clock": clock.tick()}
        else:
            pub_socket.send(msgpack.packb({
                "topic": dst, "user": src, "message": message,
                "timestamp": current_timestamp, "clock": clock.tick()
            }, use_bin_type=True))
            messages.append({"type": "private", "from": src, "to": dst, "message": message, "timestamp": current_timestamp})
            save_data(MESSAGES_FILE, messages)
            response["data"] = {"status": "OK", "timestamp": current_timestamp, "clock": clock.value}

    else:
        response["data"] = {"status": "erro", "message": "Serviço desconhecido", "timestamp": current_timestamp, "clock": clock.tick()}

    rep_socket.send(msgpack.packb(response, use_bin_type=True))
    message_counter += 1

    # HEARTBEAT
    if message_counter % 5 == 0:
        hb = {
            "service": "heartbeat",
            "data": {"user": server_name, "timestamp": datetime.now().isoformat(), "clock": clock.tick()}
        }
        ref_socket.send(msgpack.packb(hb, use_bin_type=True))
        try:
            msgpack.unpackb(ref_socket.recv(), raw=False)
        except zmq.error.Again:
            pass
