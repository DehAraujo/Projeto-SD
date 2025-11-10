import zmq from "zeromq";
import msgpack from "@msgpack/msgpack";

const nomes = [
  "Alice", "Bruna", "Carlos", "Fernanda", "Juliana",
  "Mariana", "Pedro", "Rafael", "Beatriz", "Thiago"
];
const user = nomes[Math.floor(Math.random() * nomes.length)];

const req = new zmq.Request();
const sub = new zmq.Subscriber();

// ⚙️ Conexões (ajuste as URLs conforme seu Docker Compose)
await req.connect("tcp://localhost:5555");
await sub.connect("tcp://localhost:5558");

// Se inscreve no canal "geral" e no próprio nome (para mensagens privadas)
sub.subscribe("geral");
sub.subscribe(user);

console.log(`🤖 Bot ${user} iniciado`);

(async () => {
  for await (const [topic, packed] of sub) {
    const msg = msgpack.decode(packed);

    if (msg.service === "publish") {
      const data = msg.data;
      console.log(`💬 [${data.channel}] ${data.user}: ${data.message}`);

    } else if (msg.service === "message") {
      const data = msg.data;
      if (data.dst === user) {
        console.log(`💌 (privado) ${data.src} → ${data.dst}: ${data.message}`);
      }
    }
  }
})();

// 📨 Envia mensagem pública
async function enviarPublica(msg) {
  const message = {
    service: "publish",
    data: {
      user,
      channel: "geral",
      message: msg,
      timestamp: Date.now(),
    },
  };
  await req.send(msgpack.encode(message));
  const [resp] = await req.receive();
  msgpack.decode(resp);
}

// 💬 Envia mensagem privada
async function enviarPrivada(dest, texto) {
  const message = {
    service: "message",
    data: {
      src: user,
      dst: dest,
      message: texto,
      timestamp: Date.now(),
    },
  };
  await req.send(msgpack.encode(message));
  const [resp] = await req.receive();
  msgpack.decode(resp);
}

// 🧠 Mensagens pré-definidas
const mensagens = [
  "Bom dia, galera!",
  "Tudo certo por aí?",
  "Mensagem via MessagePack 😎",
  "Alguém quer café? ☕",
  "Estou aprendendo SD 🤖",
];

// 🔁 Loop infinito enviando mensagens
while (true) {
  if (Math.random() < 0.7) {
    // pública
    const msg = mensagens[Math.floor(Math.random() * mensagens.length)];
    await enviarPublica(msg);
  } else {
    // privada
    const dest = nomes[Math.floor(Math.random() * nomes.length)];
    if (dest !== user) {
      await enviarPrivada(dest, `Oi ${dest}, sou ${user}! 👋`);
    }
  }
  await new Promise((r) => setTimeout(r, 3000 + Math.random() * 3000));
}
