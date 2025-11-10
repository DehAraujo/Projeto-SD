const zmq = require("zeromq");
const { randomUUID } = require("crypto");

const user = "bot-" + randomUUID().slice(0, 4);
const req = new zmq.Request();
const sub = new zmq.Subscriber();

// Conexões
await req.connect("tcp://server:5555");
await sub.connect("tcp://proxy:5558");

sub.subscribe(user);
sub.subscribe("geral");

console.log(`🤖 Bot ${user} iniciado`);

// Thread de recepção
(async () => {
  for await (const [msg] of sub) {
    console.log(`📥 ${user} recebeu: ${msg.toString()}`);
  }
})();

// Loop de publicação
while (true) {
  const payload = {
    service: "publish",
    data: {
      user,
      channel: "geral",
      message: `Mensagem automática de ${user}`,
      timestamp: Date.now(),
    },
  };

  await req.send(JSON.stringify(payload));
  const [reply] = await req.receive();
  console.log("📩 Resposta:", reply.toString());

  await new Promise((r) => setTimeout(r, 5000));
}
