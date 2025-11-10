# Etapa base: usa imagem oficial do Go
FROM golang:1.22

# Instala dependências do sistema para o ZeroMQ
RUN apt-get update && apt-get install -y \
    libzmq3-dev pkg-config build-essential \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do cliente Go
COPY . .

# Baixa as dependências e compila
RUN go mod tidy
RUN go build -o client main.go

# Executa o binário gerado
CMD ["./client"]
