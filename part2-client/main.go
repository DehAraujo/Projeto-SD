package part2client
package main

import (
	"encoding/json"
	"fmt"
	"time"
	"math/rand"
	zmq "github.com/pebbe/zmq4"
)

type Message struct {
	Service string                 `json:"service"`
	Data    map[string]interface{} `json:"data"`
}

func main() {
	fmt.Println("💬 Cliente Go iniciado")

	req, _ := zmq.NewSocket(zmq.REQ)
	defer req.Close()
	req.Connect("tcp://server:5555")

	sub, _ := zmq.NewSocket(zmq.SUB)
	defer sub.Close()
	sub.Connect("tcp://server:5556")

	user := fmt.Sprintf("client-%d", rand.Intn(1000))
	sub.SetSubscribe(user)
	sub.SetSubscribe("geral")

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
		fmt.Println("📩 Resposta:", resp)

		time.Sleep(3 * time.Second)
	}
}
