FROM node:20-alpine AS build

WORKDIR /app
COPY apps/viewer/package.json apps/viewer/package-lock.json* ./
RUN npm ci || npm install

COPY apps/viewer/ ./
RUN npm run build

FROM nginx:1.27-alpine

COPY apps/viewer/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
