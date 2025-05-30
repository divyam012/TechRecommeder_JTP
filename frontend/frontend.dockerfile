# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets to nginx html directory
COPY --from=build /app/build /usr/share/nginx/html


EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]