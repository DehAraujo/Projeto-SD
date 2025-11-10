const zmq = require("zeromq");

const botNames = ["Ana", "Bruno", "Carla", "Diego", "Eva", "Felipe"];

const frasesPublicas = [
  "Oi, pessoal!",
  "Como vocês estão?",
  "Alguém viu as novidades de hoje?",
  "Estou testando o sistema 😄",
  "Essa conversa está animada!",
  "Haha, muito bom!",
  "Adoro conversar com vocês!",
  "O servidor está rodando liso!",
];

const frasesPrivadas = [
  "Ei, tudo bem?",
  "Você viu o que o pessoal falou?",
  "Queria te contar uma coisa 🤫",
  "Acho que o Diego vai gostar disso!",
  "Tá curtindo o chat?",
  "Depois te chamo pra conversar melhor.",
  "Estou mandando só pra você 😉",
];

async function startBot(name) {
  const req = new zmq.Request();
  const sub = new zmq.Subscriber();

  await req.connect("tcp://server:5555");
  await sub.connect("tcp://proxy:5558");

  // Inscreve-se no canal público e no próprio nome
  sub.subscribe("geral");
  sub.subscribe(name);

  console.log(`🤖 Bot ${name} conectado!`);

  // Thread de recebimento
  (async () => {
    for await (const [msg] of sub) {
      console.log(`📥 ${name} recebeu: ${msg.toString()}`);
    }
  })();

  // Faz login no servidor
  await req.send(
    JSON.stringify({ service: "login", data: { user: name } })
  );
  await req.receive();

  // Loop de mensagens
  while (true) {
    const isPrivate = Math.random() < 0.4; // 40% chance de mensagem privada
    const timestamp = Date.now();

    if (isPrivate) {
      // Envia mensagem privada
      const dst = botNames[Math.floor(Math.random() * botNames.length)];
      if (dst === name) continue; // não envia pra si mesmo

      const message =
        frasesPrivadas[Math.floor(Math.random() * frasesPrivadas.length)];

      const payload = {
        service: "message",
        data: {
          src: name,
          dst,
          message,
          timestamp,
        },
      };

      await req.send(JSON.stringify(payload));
      const [reply] = await req.receive();
      console.log(`💌 ${name} → ${dst}: "${message}" | ${reply.toString()}`);
    } else {
      // Mensagem pública
      const message =
        frasesPublicas[Math.floor(Math.random() * frasesPublicas.length)];

      const payload = {
        service: "publish",
        data: {
          user: name,
          channel: "geral",
          message,
          timestamp,
        },
      };

      await req.send(JSON.stringify(payload));
      const [reply] = await req.receive();
      console.log(`🗣️ ${name} → geral: "${message}" | ${reply.toString()}`);
    }

    // Espera entre 3 e 8 segundos
    const delay = 3000 + Math.random() * 5000;
    await new Promise((r) => setTimeout(r, delay));
  }
}

// Inicia os bots
(async () => {
  const myName = botNames[Math.floor(Math.random() * botNames.length)];
  await startBot(myName);
})();
