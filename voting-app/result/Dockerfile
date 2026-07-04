# ── Result App ────────────────────────────────────────────
FROM node:20-slim

LABEL maintainer="Sharjik Ahamed <ahamedsarjik54@gmail.com>"
LABEL description="Result service — Node.js app that reads from PostgreSQL and displays vote results"

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY . .

EXPOSE 80

CMD ["node", "server.js"]
