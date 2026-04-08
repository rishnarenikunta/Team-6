# ---------- Build Frontend ----------
FROM node:18 AS frontend-build

WORKDIR /app/frontend
COPY frontend/my-app/package*.json ./
RUN npm install

COPY frontend/my-app .
RUN npm run build


# ---------- Final Image ----------
FROM python:3.10

# Install Node (needed to run Next start)
RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /app

# ----- Backend setup -----
COPY backend ./backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----- Frontend setup -----
COPY --from=frontend-build /app/frontend ./
RUN npm install -g next

EXPOSE 8080

CMD bash -c "\
uvicorn backend.api:app --host 0.0.0.0 --port 8000 & \
next start -p 8080 \
"