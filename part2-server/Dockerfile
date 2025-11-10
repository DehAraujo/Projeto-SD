FROM golang:1.22

WORKDIR /app

# Copia todos os arquivos do servidor
COPY . .

# Inicializa módulo Go (se ainda não existir)
RUN [ ! -f go.mod ] && go mod init server || true

# Instala dependências (como zmq4)
RUN go get github.com/pebbe/zmq4
RUN go mod tidy

# Compila o código Go
RUN go build -o server .

# Expõe as portas que o servidor usa
EXPOSE 5555 5556

# Executa o servidor compilado
CMD ["./server"]
