import zmq
import json
import time
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "channels": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def handle_request(request):
    data = load_data()
    service = request.get("service")
    payload = request.get("data", {})
    ts = payload.get("timestamp", int(time.time() * 1000))

    # LOGIN
    if service == "login":
        user = payload.get("user")
        if not user:
            return {
                "service": "login",
                "data": {"status": "erro", "timestamp": ts, "description": "Usuário não informado"}
            }
        if user not in data["users"]:
            data["users"].append(user)
            save_data(data)
        return {"service": "login", "data": {"status": "sucesso", "timestamp": ts}}

    # LISTAR USERS
    elif service == "users":
        return {"service": "users", "data": {"timestamp": ts, "users": data["users"]}}

    # CRIAR CHANNEL
    elif service == "channel":
        channel = payload.get("channel")
        if not channel:
            return {
                "service": "channel",
                "data": {"status": "erro", "timestamp": ts, "description": "Canal não informado"}
            }
        if channel not in data["channels"]:
            data["channels"].append(channel)
            save_data(data)
        return {"service": "channel", "data": {"status": "sucesso", "timestamp": ts}}

    # LISTAR CHANNELS
    elif service == "channels":
        return {"service": "channels", "data": {"timestamp": ts, "channels": data["channels"]}}

    else:
        return {
            "service": "erro",
            "data": {"timestamp": ts, "description": f"Serviço desconhecido: {service}"}
        }


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    print("🟢 Servidor Python iniciado em tcp://*:5555")

    while True:
        message = socket.recv_json()
        print(f"📩 Recebido: {message}")
        response = handle_request(message)
        print(f"📤 Enviando resposta: {response}")
        socket.send_json(response)


if __name__ == "__main__":
    main()
