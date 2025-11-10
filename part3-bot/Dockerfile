FROM node:18

WORKDIR /app

# Copia os arquivos do bot
COPY package*.json ./
RUN npm install

COPY . .

CMD ["node", "index.js"]
