FROM node:alpine3.21

WORKDIR /app

# Install dependencies first for better caching
COPY package.json package-lock.json ./
RUN npm install --include=dev

# Copy source files
COPY . .

# Generate types
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "dev"]
