FROM golang:1.20-bullseye

WORKDIR /app

# Instala libzmq e pkg-config
RUN apt-get update && apt-get install -y libzmq3-dev pkg-config

COPY go.mod ./
RUN go mod download

COPY . .

RUN go build -o client main.go

CMD ["./client"]
