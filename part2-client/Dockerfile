FROM golang:1.20
WORKDIR /app
COPY . .
RUN go mod init client && go get github.com/pebbe/zmq4 && go build -o client
CMD ["./client"]
