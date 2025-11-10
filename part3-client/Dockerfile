FROM golang:1.22

RUN apt-get update && apt-get install -y \
    libzmq3-dev pkg-config build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN go mod tidy
RUN go build -o client main.go

CMD ["./client"]
