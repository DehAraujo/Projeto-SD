FROM node:20

WORKDIR /app

# Copia dependências e instala
COPY package*.json ./
RUN npm install

# Copia o código do bot
COPY . .

# Executa o arquivo principal correto
CMD ["node", "index.js"]
