import zmq

context = zmq.Context()

# Cria os sockets de entrada e saída
frontend = context.socket(zmq.XSUB)
frontend.bind("tcp://*:5557")  # para publishers (servidor)

backend = context.socket(zmq.XPUB)
backend.bind("tcp://*:5558")   # para subscribers (clientes/bots)

print("🔁 Proxy ZeroMQ rodando nas portas 5557 (XSUB) e 5558 (XPUB)")
zmq.proxy(frontend, backend)
