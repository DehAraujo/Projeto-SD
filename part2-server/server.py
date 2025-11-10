import zmq
import json
import os
import time

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "channels": [], "messages": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def main():
    context = zmq.Context()

    # REQ/REP para comandos
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://*:5555")

    # PUB para mensagens
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect("tcp://proxy:5557")  # publica no proxy

    data = load_data()
    print("🧠 Servidor ativo em tcp://*:5555 (REQ/REP) e tcp://proxy:5557 (PUB)")

    while True:
        msg = rep_socket.recv_json()
        service = msg.get("service")
        payload = msg.get("data", {})
        now = time.time()

        if service == "login":
            user = payload.get("user")
            if user not in data["users"]:
                data["users"].append(user)
                save_data(data)
            rep_socket.send_json({"service": "login", "data": {"status": "sucesso", "timestamp": now}})

        elif service == "users":
            rep_socket.send_json({"service": "users", "data": {"users": data["users"], "timestamp": now}})

        elif service == "channel":
            channel = payload.get("channel")
            if channel not in data["channels"]:
                data["channels"].append(channel)
                save_data(data)
                rep_socket.send_json({"service": "channel", "data": {"status": "sucesso", "timestamp": now}})
            else:
                rep_socket.send_json({"service": "channel", "data": {"status": "erro", "message": "Canal já existe", "timestamp": now}})

        elif service == "channels":
            rep_socket.send_json({"service": "channels", "data": {"channels": data["channels"], "timestamp": now}})

        elif service == "publish":
            user = payload.get("user")
            channel = payload.get("channel")
            message = payload.get("message")

            if channel not in data["channels"]:
                rep_socket.send_json({"service": "publish", "data": {"status": "erro", "message": "Canal inexistente", "timestamp": now}})
            else:
                pub_socket.send_string(f"{channel} {user}: {message}")
                data["messages"].append({"type": "channel", "channel": channel, "user": user, "message": message, "timestamp": now})
                save_data(data)
                rep_socket.send_json({"service": "publish", "data": {"status": "OK", "timestamp": now}})

        elif service == "message":
            src = payload.get("src")
            dst = payload.get("dst")
            message = payload.get("message")

            if dst not in data["users"]:
                rep_socket.send_json({"service": "message", "data": {"status": "erro", "message": "Usuário inexistente", "timestamp": now}})
            else:
                pub_socket.send_string(f"{dst} {src}: {message}")
                data["messages"].append({"type": "direct", "src": src, "dst": dst, "message": message, "timestamp": now})
                save_data(data)
                rep_socket.send_json({"service": "message", "data": {"status": "OK", "timestamp": now}})

        else:
            rep_socket.send_json({"service": "erro", "data": {"message": f"Serviço desconhecido: {service}", "timestamp": now}})

if __name__ == "__main__":
    main()
