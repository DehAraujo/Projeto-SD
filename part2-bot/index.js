const zmq = require("zeromq");
const { randomUUID } = require("crypto");

(async () => {
  const user = "bot-" + randomUUID().slice(0, 4);

  const req = new zmq.Request();
  await req.connect("tcp://server:5555");

  const sub = new zmq.Subscriber();
  await sub.connect("tcp://server:5556");
  sub.subscribe(user);
  sub.subscribe("geral");

  console.log(`🤖 Bot ${user} iniciado`);

  while (true) {
    const msg = {
      service: "publish",
      data: {
        user,
        channel: "geral",
        message: `Mensagem do ${user}`,
        timestamp: Date.now(),
      },
    };

    await req.send(JSON.stringify(msg));
    const [reply] = await req.receive();
    console.log("📩 Resposta:", reply.toString());

    await new Promise(r => setTimeout(r, 5000));
  }
})();
