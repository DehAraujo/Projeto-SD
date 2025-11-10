import zmq
import msgpack
import os
import time

DATA_FILE = "/data/data.dat"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "channels": ["geral"], "messages": []}
    try:
        with open(DATA_FILE, "rb") as f:
            return msgpack.unpackb(f.read(), raw=False)
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return {"users": [], "channels": ["geral"], "messages": []}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "wb") as f:
        f.write(msgpack.packb(data, use_bin_type=True))

def main():
    ctx = zmq.Context()

    rep = ctx.socket(zmq.REP)
    rep.bind("tcp://*:5555")

    pub = ctx.socket(zmq.PUB)
    pub.connect("tcp://proxy:5557")

    print("🧠 Servidor MessagePack ativo em tcp://*:5555 e tcp://proxy:5557")

    data = load_data()

    while True:
        msg_bytes = rep.recv()
        msg = msgpack.unpackb(msg_bytes, raw=False)

        service = msg.get("service")
        payload = msg.get("data", {})
        now = int(time.time() * 1000)

        response = {}

        if service == "login":
            user = payload.get("user")
            if user and user not in data["users"]:
                data["users"].append(user)
                save_data(data)
            response = {"status": "OK", "timestamp": now}

        elif service == "publish":
            user = payload.get("user")
            channel = payload.get("channel", "geral")
            message = payload.get("message")

            if channel not in data["channels"]:
                response = {"status": "erro", "message": f"Canal '{channel}' não existe"}
            else:
                pub_data = {"user": user, "message": message, "timestamp": now}
                pub.send_multipart([
                    channel.encode(),
                    msgpack.packb(pub_data, use_bin_type=True)
                ])
                data["messages"].append(pub_data)
                save_data(data)
                response = {"status": "OK", "timestamp": now}

        else:
            response = {"status": "erro", "message": f"Serviço desconhecido: {service}"}

        rep.send(msgpack.packb({"service": service, "data": response}, use_bin_type=True))

if __name__ == "__main__":
    main()
