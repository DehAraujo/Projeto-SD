import zmq
import msgpack
from datetime import datetime

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5558")
sub.setsockopt_string(zmq.SUBSCRIBE, "geral")

print("🛰️ Monitor escutando canal [geral]...")

while True:
    topic, packed = sub.recv_multipart()
    msg = msgpack.unpackb(packed, raw=False)
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"💬 [{topic.decode()}] {msg['user']}: {msg['message']} ({ts})")
