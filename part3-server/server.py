import zmq
import msgpack
import msgpack_numpy as m
import os, time, json

DATA_FILE = "data/data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "channels": ["geral"], "messages": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def main():
    ctx = zmq.Context()
    rep = ctx.socket(zmq.REP)
    pub = ctx.socket(zmq.PUB)
    rep.bind("tcp://*:5555")
    pub.connect("tcp://proxy:5557")

    print("🧠 Servidor MessagePack ativo em tcp://*:5555")
    data = load_data()

    while True:
        msg_bytes = rep.recv()
        msg = msgpack.unpackb(msg_bytes, raw=False)
        service = msg.get("service")
        payload = msg.get("data", {})
        now = int(time.time() * 1000)

        if service == "login":
            user = payload.get("user")
            if user and user not in data["users"]:
                data["users"].append(user)
                save_data(data)
            rep.send(msgpack.packb({"service": "login", "data": {"status": "OK", "timestamp": now}}, use_bin_type=True))

        elif service == "channel":
            channel = payload.get("channel")
            if not channel:
                rep.send(msgpack.packb({"service": "channel", "data": {"status": "erro", "message": "Canal inválido"}}, use_bin_type=True))
            elif channel not in data["channels"]:
                data["channels"].append(channel)
                save_data(data)
                rep.send(msgpack.packb({"service": "channel", "data": {"status": "OK", "timestamp": now}}, use_bin_type=True))
            else:
                rep.send(msgpack.packb({"service": "channel", "data": {"status": "erro", "message": "Canal já existe"}}, use_bin_type=True))

        elif service == "publish":
            user = payload.get("user")
            channel = payload.get("channel")
            message = payload.get("message")
            pub.send_string(f"{channel} {user}: {message}")
            rep.send(msgpack.packb({"service": "publish", "data": {"status": "OK", "timestamp": now}}, use_bin_type=True))

        elif service == "message":
            src = payload.get("src")
            dst = payload.get("dst")
            message = payload.get("message")
            pub.send_string(f"{dst} {src}: {message}")
            rep.send(msgpack.packb({"service": "message", "data": {"status": "OK", "timestamp": now}}, use_bin_type=True))

        else:
            rep.send(msgpack.packb({"service": "erro", "data": {"message": "Serviço desconhecido"}}, use_bin_type=True))

if __name__ == "__main__":
    main()
