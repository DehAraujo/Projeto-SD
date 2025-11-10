import zmq
import json
import os
import time

# Caminho correto para o arquivo persistente
DATA_FILE = "data/data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "channels": [], "messages": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    # Garante que o diretório exista
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def main():
    ctx = zmq.Context()

    rep = ctx.socket(zmq.REP)
    rep.bind("tcp://*:5555")

    pub = ctx.socket(zmq.PUB)
    pub.connect("tcp://proxy:5557")

    print("🧠 Servidor ativo em tcp://*:5555 (REQ/REP) e tcp://proxy:5557 (PUB)")

    data = load_data()

    while True:
        msg_raw = rep.recv_string()
        msg = json.loads(msg_raw)
        service = msg.get("service")
        payload = msg.get("data", {})
        now = int(time.time() * 1000)

        if service == "login":
            user = payload.get("user")
            if user and user not in data["users"]:
                data["users"].append(user)
                save_data(data)
            rep.send_json({"service": "login", "data": {"status": "OK", "timestamp": now}})

        elif service == "channel":
            channel = payload.get("channel") or payload.get("name")
            if not channel:
                rep.send_json({"service": "channel", "data": {"status": "erro", "message": "Canal inválido", "timestamp": now}})
            elif channel not in data["channels"]:
                data["channels"].append(channel)
                save_data(data)
                rep.send_json({"service": "channel", "data": {"status": "OK", "timestamp": now}})
            else:
                rep.send_json({"service": "channel", "data": {"status": "erro", "message": "Canal já existe", "timestamp": now}})

        elif service == "publish":
            user = payload.get("user")
            channel = payload.get("channel")
            message = payload.get("message")

            if channel not in data["channels"]:
                rep.send_json({"service": "publish", "data": {"status": "erro", "message": f"Canal '{channel}' não existe", "timestamp": now}})
            else:
                pub.send_string(f"{channel} {user}: {message}")
                data["messages"].append({"type": "channel", "channel": channel, "user": user, "message": message, "timestamp": now})
                save_data(data)
                rep.send_json({"service": "publish", "data": {"status": "OK", "timestamp": now}})

        elif service == "message":
            src = payload.get("src")
            dst = payload.get("dst")
            message = payload.get("message")

            if dst not in data["users"]:
                rep.send_json({"service": "message", "data": {"status": "erro", "message": f"Usuário '{dst}' não existe", "timestamp": now}})
            else:
                pub.send_string(f"{dst} {src}: {message}")
                data["messages"].append({"type": "direct", "src": src, "dst": dst, "message": message, "timestamp": now})
                save_data(data)
                rep.send_json({"service": "message", "data": {"status": "OK", "timestamp": now}})

        else:
            rep.send_json({"service": "erro", "data": {"message": f"Serviço desconhecido: {service}", "timestamp": now}})


if __name__ == "__main__":
    main()
