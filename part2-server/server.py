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

    // Socket REQ para enviar comandos ao servidor
    req, _ := zmq.NewSocket(zmq.REQ)
    defer req.Close()
    req.Connect("tcp://server:5555")

    // Socket SUB para receber mensagens
    sub, _ := zmq.NewSocket(zmq.SUB)
    defer sub.Close()
    sub.Connect("tcp://server:5556")

    user := fmt.Sprintf("client-%d", rand.Intn(1000))

    // Subscreve no canal "geral"
    sub.SetSubscribe("geral")

    fmt.Println("✅ Subscrito no canal 'geral' como", user)

    // LOOP de publicação
    go func() {
        for {
            msg := Message{
                Service: "publish",
                Data: map[string]interface{}{
                    "user":      user,
                    "channel":   "geral",
                    "message":   fmt.Sprintf("Olá do %s!", user),
                    "timestamp": time.Now().UnixMilli(),
                },
            }

            bytes, _ := json.Marshal(msg)
            req.Send(string(bytes), 0)

            resp, _ := req.Recv(0)
            fmt.Println("📩 Resposta servidor:", resp)

            time.Sleep(3 * time.Second)
        }
    }()

    // LOOP para receber mensagens
    for {
        if sub.Poll(time.Second*1, zmq.POLLIN) > 0 {
            msg, _ := sub.Recv(0)
            fmt.Println("📥 Recebido via SUB:", msg)
        }
    }
}
