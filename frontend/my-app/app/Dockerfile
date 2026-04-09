FROM node:20-bullseye AS build

WORKDIR /app
COPY frontend/my-app/package*.json ./
RUN npm install
COPY frontend/my-app ./
RUN npm run build

FROM node:20-bullseye
WORKDIR /app
COPY --from=build /app ./

ENV PORT=8080
EXPOSE 8080

CMD ["npm", "run", "start"]