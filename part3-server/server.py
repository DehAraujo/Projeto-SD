import zmq
import msgpack
import os
import json
from datetime import datetime

# --- Diretórios e Arquivos de Persistência ---
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

# Cria pasta de dados se não existir
os.makedirs(DATA_DIR, exist_ok=True)

# --- Funções de persistência ---
def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Aviso: {file} corrompido ou vazio. Reiniciando.")
            return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# --- Estado Global em Memória ---
users = load_data(USERS_FILE)
channels = load_data(CHANNELS_FILE)
messages = load_data(MESSAGES_FILE)

# --- Sockets ZMQ ---
context = zmq.Context()
rep_socket = context.socket(zmq.REP)
rep_socket.bind("tcp://*:5556")
pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://proxy:5557")

print("🧠 Servidor parte 3 iniciado (MessagePack com cache em memória)")

# --- Loop Principal ---
while True:
    try:
        raw_msg = rep_socket.recv()
        msg = msgpack.unpackb(raw_msg, raw=False)
    except Exception as e:
        print(f"Erro ao receber mensagem REQ: {e}")
        continue

    service = msg.get("service")
    data = msg.get("data", {})
    response = {"service": service, "data": {}}
    current_timestamp = datetime.now().isoformat()

    # === LOGIN ===
    if service == "login":
        user = data.get("user")
        if user not in users:
            users.append(user)
            save_data(USERS_FILE, users)
        response["data"] = {"status": "sucesso", "timestamp": current_timestamp}

    # === USERS ===
    elif service == "users":
        response["data"] = {"users": users, "timestamp": current_timestamp}

    # === CRIAR/VALIDAR CANAL ===
    elif service == "channel":
        channel = data.get("channel")
        if channel not in channels:
            channels.append(channel)
            save_data(CHANNELS_FILE, channels)
            response["data"] = {"status": "sucesso", "timestamp": current_timestamp}
        else:
            response["data"] = {"status": "sucesso", "message": "Canal já existe", "timestamp": current_timestamp}

    # === LISTAR CANAIS ===
    elif service == "channels":
        response["data"] = {"channels": channels, "timestamp": current_timestamp}

    # === PUBLICAR EM CANAL ===
    elif service == "publish":
        user = data.get("user")
        channel = data.get("channel")
        message = data.get("message")

        if channel not in channels:
            response["data"] = {"status": "erro", "message": "Canal inexistente", "timestamp": current_timestamp}
        else:
            pub_message_data = {
                "topic": channel,
                "user": user,
                "message": message,
                "timestamp": current_timestamp
            }
            pub_socket.send(msgpack.packb(pub_message_data, use_bin_type=True))

            messages.append({
                "type": "channel",
                "from": user,
                "to": channel,
                "message": message,
                "timestamp": current_timestamp
            })
            save_data(MESSAGES_FILE, messages)
            response["data"] = {"status": "OK", "timestamp": current_timestamp}

    # === MENSAGEM PRIVADA ===
    elif service == "message":
        src = data.get("src")
        dst = data.get("dst")
        message = data.get("message")

        # ✅ Aceita mesmo que o destino ainda não tenha logado
        pub_message_data = {
            "topic": dst,
            "user": src,
            "message": message,
            "timestamp": current_timestamp
        }
        pub_socket.send(msgpack.packb(pub_message_data, use_bin_type=True))

        messages.append({
            "type": "private",
            "from": src,
            "to": dst,
            "message": message,
            "timestamp": current_timestamp
        })
        save_data(MESSAGES_FILE, messages)

        response["data"] = {"status": "OK", "timestamp": current_timestamp}

    # === SERVIÇO DESCONHECIDO ===
    else:
        response["data"] = {"status": "erro", "message": "Serviço desconhecido", "timestamp": current_timestamp}

    # --- Envia resposta ---
    rep_socket.send(msgpack.packb(response, use_bin_type=True))
