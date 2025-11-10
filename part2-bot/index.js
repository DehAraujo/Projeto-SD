const zmq = require("zeromq");
const { randomInt } = require("crypto"); 

const REQ_ADDR = "tcp://server:5556";
const SUB_ADDR = "tcp://proxy:5558";

const users = ["Ana", "Bruno", "Carlos", "Diana", "Eduardo"];
const channels = ["geral", "dev", "games", "random", "suporte", "offtopic"];
const mensagens = [
  "Olá pessoal!",
  "Alguém aí?",
  "Trabalhando no projeto 😎",
  "ZeroMQ é top!",
  "Testando mensagens automáticas",
  "Pub/Sub funcionando!",
  "Vamos jogar depois?",
  "Bug resolvido 🎉",
  "Mensagem de teste",
  "Enviando mais uma!"
];

async function main() {
  const username = users[randomInt(users.length)];
  console.log(`🤖 Bot iniciado como: ${username}`);

  const req = new zmq.Request();
  await req.connect(REQ_ADDR);

  const sub = new zmq.Subscriber();
  await sub.connect(SUB_ADDR);

  // --- 1. LOGIN ---
  console.log(`💬 Enviando login para ${username}...`);
  await req.send(JSON.stringify({ service: "login", data: { user: username, timestamp: new Date().toISOString() } }));
  const loginReply = await req.receive();
  console.log(`✅ Login Status: ${loginReply.toString()}`);

  // --- 2. CRIAÇÃO/VALIDAÇÃO DE CANAIS ---
  console.log("🛠️ Criando/Validando canais...");
  for (const ch of channels) {
    const channelMsg = {
        service: "channel",
        data: {
            channel: ch,
            user: username,
            action: "create", 
            timestamp: new Date().toISOString(),
        },
    };
    await req.send(JSON.stringify(channelMsg));
    const [channelReply] = await req.receive();
    console.log(`   Canal ${ch} → Confirmação: ${channelReply.toString()}`);
  }

  // --- 3. SUBSCRIÇÃO ---
  sub.subscribe(username); // Subscreve no nome de usuário (para privadas)
  channels.forEach(c => sub.subscribe(c));

  // --- 4. THREAD PARA OUVIR MENSAGENS (Subscriber) ---
  (async () => {
    try {
      for await (const [msg] of sub) {
        const fullMessage = msg.toString();
        console.log(`📨 (${username}) recebeu: ${fullMessage}`);
      }
    } catch (e) {
      console.error(`Erro no loop de subscrição: ${e}`);
    }
  })();

  // --- 5. LOOP DE PUBLICAÇÃO E MENSAGEM PRIVADA (CORRIGIDO) ---
  while (true) {
    let isPrivate = randomInt(100) < 30;
    const text = mensagens[randomInt(mensagens.length)];
    let msg, logMessage;

    if (isPrivate) {
        // === MENSAGEM PRIVADA (SERVICE: message) ===
        const dstUser = users[randomInt(users.length)];
        
        // Evita que o bot envie mensagem privada para si mesmo
        if (dstUser !== username) { 
            msg = {
                service: "message",
                data: {
                    src: username, // Usuário de origem
                    dst: dstUser,  // Usuário de destino (Tópico de PUB)
                    message: text,
                    timestamp: new Date().toISOString(),
                },
            };
            logMessage = `✉️ (${username}) enviou PRIVADO para ${dstUser}: "${text}"`;
        } else {
            // Se for para si mesmo, trata como uma publicação em canal para não perder a iteração
             isPrivate = false;
        }

    } 
    
    if (!isPrivate) {
        // === PUBLICAÇÃO EM CANAL (SERVICE: publish) ===
        const ch = channels[randomInt(channels.length)];
        msg = {
            service: "publish",
            data: {
                user: username,
                channel: ch,
                message: text,
                timestamp: new Date().toISOString(),
            },
        };
        logMessage = `💬 (${username}) publicou em ${ch}: "${text}"`;
    }

    // Envio REQ para o servidor e Recebe a confirmação (Se msg não for nula)
    if (msg) {
        await req.send(JSON.stringify(msg));
        const [reply] = await req.receive();
        
        console.log(`${logMessage} → Confirmação: ${reply.toString()}`);
    }
    
    // Aguarda um tempo antes da próxima mensagem
    await new Promise(r => setTimeout(r, randomInt(500, 2000))); 
  }
}

main().catch(console.error);