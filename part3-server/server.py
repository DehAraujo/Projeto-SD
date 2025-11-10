import zmq
import msgpack

ctx = zmq.Context()

# REQ/REP — para receber requisições dos clientes e bots
rep = ctx.socket(zmq.REP)
rep.bind("tcp://*:5556")

# PUB/SUB — para enviar mensagens públicas e privadas
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5557")

print("🧠 Servidor pronto — trocando mensagens com MessagePack...")

while True:
    packed = rep.recv()
    msg = msgpack.unpackb(packed, raw=False)
    service = msg.get("service")
    data = msg.get("data", {})
    user = data.get("user")

    # --- PUBLICAÇÃO EM CANAL ---
    if service == "publish":
        channel = data["channel"]
        message = data["message"]
        payload = {
            "service": "publish",
            "data": {
                "user": user,
                "channel": channel,
                "message": message,
                "timestamp": data["timestamp"],
            },
        }

        # Envia para todos os inscritos no canal
        pub.send_multipart([channel.encode(), msgpack.packb(payload)])
        rep.send(msgpack.packb({
            "service": "publish",
            "data": {"status": "OK", "timestamp": data["timestamp"]},
        }))

    # --- MENSAGEM PRIVADA ---
    elif service == "message":
        src = data["src"]
        dst = data["dst"]
        message = data["message"]

        payload = {
            "service": "message",
            "data": {
                "src": src,
                "dst": dst,
                "message": message,
                "timestamp": data["timestamp"],
            },
        }

        # Publica no tópico com o nome do destinatário
        pub.send_multipart([dst.encode(), msgpack.packb(payload)])
        rep.send(msgpack.packb({
            "service": "message",
            "data": {"status": "OK", "timestamp": data["timestamp"]},
        }))

    # --- SERVIÇO DESCONHECIDO ---
    else:
        rep.send(msgpack.packb({
            "service": "erro",
            "data": {"message": "Serviço inválido"},
        }))
