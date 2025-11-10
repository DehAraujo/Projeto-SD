import zmq from "zeromq";
import msgpack from "msgpack-lite";

async function start() {
  const req = new zmq.Request();
  await req.connect("tcp://server:5555");
  const user = "bot-js";

  // Login via MessagePack
  await req.send(msgpack.encode({ service: "login", data: { user } }));
  const [reply] = await req.receive();
  console.log("🤖 Login:", msgpack.decode(reply));

  // Publish loop
  while (true) {
    const msg = {
      service: "publish",
      data: { user, channel: "geral", message: "Mensagem binária 🔥", timestamp: Date.now() },
    };
    await req.send(msgpack.encode(msg));
    const [resp] = await req.receive();
    console.log("📤 Resposta:", msgpack.decode(resp));
    await new Promise(r => setTimeout(r, 3000));
  }
}

start();
