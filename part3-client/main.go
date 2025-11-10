package main

import (
	"fmt"
	"log"
	"math/rand"
	"time"

	zmq "github.com/pebbe/zmq4"
	"github.com/vmihailenco/msgpack/v5"
)

type Message struct {
	Service string                 `msgpack:"service"`
	Data    map[string]interface{} `msgpack:"data"`
}

func main() {
	rand.Seed(time.Now().UnixNano())
	user := fmt.Sprintf("client-%d", rand.Intn(100))
	fmt.Printf("💻 Cliente %s iniciado\n", user)

	// --- Socket REQ (para enviar requisições ao servidor) ---
	req, err := zmq.NewSocket(zmq.REQ)
	if err != nil {
		log.Fatal(err)
	}
	defer req.Close()
	req.Connect("tcp://proxy:5555")

	// --- Socket SUB (para receber mensagens publicadas) ---
	sub, err := zmq.NewSocket(zmq.SUB)
	if err != nil {
		log.Fatal(err)
	}
	defer sub.Close()
	sub.Connect("tcp://proxy:5558")

	// Inscreve-se no canal "geral" e no tópico do próprio usuário
	sub.SetSubscribe("geral")
	sub.SetSubscribe(user)

	// --- Goroutine que recebe mensagens ---
	go func() {
		for {
			msgParts, err := sub.RecvMessageBytes(0)
			if err != nil {
				log.Println("Erro ao receber mensagem:", err)
				continue
			}
			if len(msgParts) < 2 {
				continue
			}

			topic := string(msgParts[0])
			packed := msgParts[1]

			var msg Message
			if err := msgpack.Unmarshal(packed, &msg); err != nil {
				log.Println("Erro ao decodificar msgpack:", err)
				continue
			}

			data := msg.Data
			switch msg.Service {
			case "publish":
				fmt.Printf("💬 [%s] %s: %s\n", topic, data["user"], data["message"])
			case "message":
				fmt.Printf("💌 (privado) %s → %s: %s\n", data["src"], data["dst"], data["message"])
			default:
				fmt.Printf("📦 [%s] Mensagem desconhecida: %+v\n", topic, msg)
			}
		}
	}()

	// --- Loop principal: alterna entre mensagem pública e privada ---
	for {
		// 50% chance de enviar pública, 50% privada
		if rand.Intn(2) == 0 {
			sendPublic(req, user)
		} else {
			sendPrivate(req, user)
		}
		time.Sleep(time.Duration(rand.Intn(4000)+3000) * time.Millisecond)
	}
}

func sendPublic(req *zmq.Socket, user string) {
	msg := Message{
		Service: "publish",
		Data: map[string]interface{}{
			"user":      user,
			"channel":   "geral",
			"message":   fmt.Sprintf("Olá do %s 👋", user),
			"timestamp": time.Now().UnixMilli(),
		},
	}
	sendAndLog(req, msg)
}

func sendPrivate(req *zmq.Socket, user string) {
	dst := fmt.Sprintf("client-%d", rand.Intn(100))
	if dst == user {
		dst = "client-0"
	}
	msg := Message{
		Service: "message",
		Data: map[string]interface{}{
			"src":       user,
			"dst":       dst,
			"message":   fmt.Sprintf("Oi %s, tudo bem? 😄", dst),
			"timestamp": time.Now().UnixMilli(),
		},
	}
	sendAndLog(req, msg)
}

func sendAndLog(req *zmq.Socket, msg Message) {
	bytes, _ := msgpack.Marshal(msg)
	req.SendBytes(bytes, 0)
	resp, _ := req.RecvBytes(0)

	var reply Message
	msgpack.Unmarshal(resp, &reply)

	status := reply.Data["status"]
	if status == "OK" {
		fmt.Printf("📤 [%s] enviado com sucesso!\n", msg.Service)
	} else {
		fmt.Printf("⚠️  Erro ao enviar %s: %v\n", msg.Service, reply.Data["message"])
	}
}
