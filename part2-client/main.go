package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"time"

	zmq "github.com/pebbe/zmq4"
)

type Message struct {
	Service string                 `json:"service"`
	Data    map[string]interface{} `json:"data"`
}

func main() {
	fmt.Println("💬 Cliente Go iniciado")

	// 1. SETUP DO SOCKET REQ (Request/Reply)
	req, err := zmq.NewSocket(zmq.REQ)
	if err != nil {
		fmt.Println("Erro ao criar socket REQ:", err)
		return
	}
	defer req.Close()
	req.Connect("tcp://server:5555")

	// 2. SETUP DO SOCKET SUB (Subscriber)
	sub, err := zmq.NewSocket(zmq.SUB)
	if err != nil {
		fmt.Println("Erro ao criar socket SUB:", err)
		return
	}
	defer sub.Close()
	sub.Connect("tcp://server:5556")

	// Gerar usuário e assinar tópicos
	rand.Seed(time.Now().UnixNano())
	user := fmt.Sprintf("client-%d", rand.Intn(1000))
	sub.SetSubscribe(user)
	sub.SetSubscribe("geral")

	// --- FASE DE SETUP (REQ/REP) ---

	// A. LOGIN DO USUÁRIO
	loginMsg := Message{
		Service: "login",
		Data: map[string]interface{}{
			"user":      user,
			"timestamp": time.Now().UnixMilli(),
		},
	}
	bytes, _ := json.Marshal(loginMsg)
	req.Send(string(bytes), 0)
	resp, _ := req.Recv(0)
	fmt.Println("📩 Resposta Login:", resp)

	// B. CRIAÇÃO DO CANAL "geral"
	createChannelMsg := Message{
		Service: "channel",
		Data: map[string]interface{}{
			"channel":   "geral",
			"timestamp": time.Now().UnixMilli(),
		},
	}
	bytes, _ = json.Marshal(createChannelMsg)
	req.Send(string(bytes), 0)
	resp, _ = req.Recv(0)
	fmt.Println("📡 Resposta Criação Canal:", resp)

	// --- FASE DE LOOP (PUB/SUB / EXECUÇÃO) ---

	for {
		msg := Message{
			Service: "publish",
			Data: map[string]interface{}{
				"user":      user,
				"channel":   "geral",
				"message":   fmt.Sprintf("Olá de %s!", user),
				"timestamp": time.Now().UnixMilli(),
			},
		}

		bytes, _ := json.Marshal(msg)
		req.Send(string(bytes), 0)
		resp, _ := req.Recv(0)
		fmt.Println("📩 Resposta Publicação:", resp)

		time.Sleep(3 * time.Second)
	}
}
