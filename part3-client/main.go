package main

import (
	"fmt"
	"time"

	zmq "github.com/pebbe/zmq4"
	"github.com/vmihailenco/msgpack/v5"
)

type Message struct {
	Service string                 `msgpack:"service"`
	Data    map[string]interface{} `msgpack:"data"`
}

func main() {
	req, _ := zmq.NewSocket(zmq.REQ)
	defer req.Close()
	req.Connect("tcp://server:5555")

	user := "client-go"

	login := Message{
		Service: "login",
		Data: map[string]interface{}{
			"user":      user,
			"timestamp": time.Now().UnixMilli(),
		},
	}
	sendMsgPack(req, login)
	resp := recvMsgPack(req)
	fmt.Println("📥 Login:", resp)

	pub := Message{
		Service: "publish",
		Data: map[string]interface{}{
			"user":      user,
			"channel":   "geral",
			"message":   "Olá via MessagePack!",
			"timestamp": time.Now().UnixMilli(),
		},
	}
	sendMsgPack(req, pub)
	resp = recvMsgPack(req)
	fmt.Println("📥 Publicação:", resp)
}

func sendMsgPack(socket *zmq.Socket, msg Message) {
	data, _ := msgpack.Marshal(msg)
	socket.SendBytes(data, 0)
}

func recvMsgPack(socket *zmq.Socket) Message {
	reply, _ := socket.RecvBytes(0)
	var resp Message
	msgpack.Unmarshal(reply, &resp)
	return resp
}
