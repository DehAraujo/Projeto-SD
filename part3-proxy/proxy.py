import zmq
import threading

ctx = zmq.Context()

# Proxy REQ/REP — liga bots/clientes (REQ) com servidor (REP)
def reqrep_proxy():
    frontend = ctx.socket(zmq.ROUTER)
    backend = ctx.socket(zmq.DEALER)
    frontend.bind("tcp://*:5555")  # clientes/bots enviam
    backend.bind("tcp://*:5556")   # servidor recebe
    print("🔁 Proxy REQ/REP rodando (5555 ↔ 5556)")
    zmq.proxy(frontend, backend)

# Proxy PUB/SUB — liga servidor (PUB) com bots/monitores (SUB)
def pubsub_proxy():
    xsub = ctx.socket(zmq.XSUB)
    xpub = ctx.socket(zmq.XPUB)
    xsub.bind("tcp://*:5557")  # servidor publica
    xpub.bind("tcp://*:5558")  # clientes/bots/monitores escutam
    print("📡 Proxy PUB/SUB rodando (5557 ↔ 5558)")
    zmq.proxy(xsub, xpub)

threading.Thread(target=reqrep_proxy, daemon=True).start()
pubsub_proxy()
