# ---------- Build React ----------
FROM node:18 AS build

WORKDIR /app
COPY frontend/my-app/package*.json ./
RUN npm install

COPY frontend/my-app .
RUN npm run build


# ---------- Production image ----------
FROM node:18

WORKDIR /app
RUN npm install -g serve

COPY --from=build /app/build ./build

EXPOSE 8080
CMD ["serve", "-s", "build", "-l", "8080"]