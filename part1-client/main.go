package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/pebbe/zmq4"
)

type Message struct {
	Service string                 `json:"service"`
	Data    map[string]interface{} `json:"data"`
}

func sendRequest(socket *zmq4.Socket, msg Message) (Message, error) {
	data, err := json.Marshal(msg)
	if err != nil {
		return Message{}, err
	}
	_, err = socket.SendBytes(data, 0)
	if err != nil {
		return Message{}, err
	}

	replyBytes, err := socket.RecvBytes(0)
	if err != nil {
		return Message{}, err
	}

	var reply Message
	if err := json.Unmarshal(replyBytes, &reply); err != nil {
		return Message{}, err
	}

	return reply, nil
}

func now() int64 {
	return time.Now().UnixMilli()
}

func main() {
	// Conecta ao servidor Python
	socket, err := zmq4.NewSocket(zmq4.REQ)
	if err != nil {
		log.Fatal(err)
	}
	defer socket.Close()

	serverAddr := "tcp://server:5555"
	fmt.Println("🔗 Conectando ao servidor em", serverAddr)
	err = socket.Connect(serverAddr)
	if err != nil {
		log.Fatal(err)
	}

	// 1️⃣ LOGIN
	loginReq := Message{
		Service: "login",
		Data: map[string]interface{}{
			"user":      "client-go",
			"timestamp": now(),
		},
	}
	fmt.Println("📤 Enviando login:", loginReq)
	loginResp, err := sendRequest(socket, loginReq)
	if err != nil {
		log.Fatal("Erro no login:", err)
	}
	fmt.Println("📩 Resposta login:", loginResp)

	// 2️⃣ LISTAR USUÁRIOS
	usersReq := Message{
		Service: "users",
		Data: map[string]interface{}{
			"timestamp": now(),
		},
	}
	fmt.Println("📤 Pedindo lista de usuários...")
	usersResp, err := sendRequest(socket, usersReq)
	if err != nil {
		log.Fatal("Erro ao listar usuários:", err)
	}
	fmt.Println("📩 Usuários cadastrados:", usersResp.Data["users"])

	// 3️⃣ CRIAR CANAL
	channelReq := Message{
		Service: "channel",
		Data: map[string]interface{}{
			"channel":   "geral",
			"timestamp": now(),
		},
	}
	fmt.Println("📤 Criando canal 'geral'...")
	channelResp, err := sendRequest(socket, channelReq)
	if err != nil {
		log.Fatal("Erro ao criar canal:", err)
	}
	fmt.Println("📩 Resposta criação canal:", channelResp)

	// 4️⃣ LISTAR CANAIS
	channelsReq := Message{
		Service: "channels",
		Data: map[string]interface{}{
			"timestamp": now(),
		},
	}
	fmt.Println("📤 Pedindo lista de canais...")
	channelsResp, err := sendRequest(socket, channelsReq)
	if err != nil {
		log.Fatal("Erro ao listar canais:", err)
	}
	fmt.Println("📩 Canais disponíveis:", channelsResp.Data["channels"])

	fmt.Println("✅ Cliente Go finalizou com sucesso!")
}
