# 🐳 Deploying **Magical Oracle** with Docker Compose

This folder packages the challenge into a self-contained Docker image and a minimal `docker-compose.yml`.  The service listens on **TCP 1338** and is production-ready (supervisord + socat).

---
## 1. Files
| file | purpose |
|------|---------|
| `Dockerfile` | Builds the image (`python:3.13-slim`, installs socat/supervisord, copies challenge) |
| `docker-compose.yml` | One-service stack exposing port 1338 |
| `chal.py` | Challenge logic (unchanged) |
| `flag.txt` | Hidden flag shipped inside the container |
| `run.sh` | wrapper that runs `chal.py` behind socat |
| `supervisord.conf` | keeps socat alive |

---
## 2. Quick start
```bash
# build the image & start the service
docker compose up --build -d

# verify (should print the banner)
nc localhost 1338
```
To stop and remove the container:
```bash
docker compose down
```

---
## 3. Manual (without Compose)
```bash
# build image manually
docker build -t magical_oracle .

# run it
docker run -d -p 1338:1338 --name magical_oracle magical_oracle
```

---
## 4. Development notes
* It works for me and:

```bash
sage --version
SageMath version 10.4, Release Date: 2024-07-19
```
So, if you have local issues with any scripts. Tough.