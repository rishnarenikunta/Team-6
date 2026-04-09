# ---------- Base image with Node + Python ----------
FROM node:20-bullseye

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

# ---------- Copy backend ----------
COPY frontend/my-app/app ./backend
COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

# ---------- Copy frontend ----------
WORKDIR /app/frontend/my-app
COPY frontend/my-app/package*.json ./
RUN npm install
COPY frontend/my-app ./

# ---------- Environment ----------
ENV PYTHONPATH=/app
ENV PORT=8080
EXPOSE 8080

# ---------- Start BOTH servers ----------
CMD bash -c "\
  uvicorn backend.api:app --host 0.0.0.0 --port 8000 & \
  npm run dev -- -p 8080 -H 0.0.0.0 \
"