FROM node:20-alpine

WORKDIR /app

# Install dependencies first (cached layer)
COPY package.json ./
RUN npm install --no-audit --no-fund --loglevel=error

# Config files
COPY tsconfig.json next.config.mjs tailwind.config.ts postcss.config.js next-env.d.ts ./

# App source (volume-mounted in compose for live reload, but copied for production build)
COPY app ./app
COPY components ./components
COPY lib ./lib
COPY public ./public

EXPOSE 3000

CMD ["npm", "run", "dev"]
