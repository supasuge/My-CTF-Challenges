# Dockerfile
FROM python:3.13-slim

# 1) Install runtime deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends socat supervisor dos2unix \
 && rm -rf /var/lib/apt/lists/*

# 2) Set up work dir
WORKDIR /opt/app

# 3) Copy challenge and support files
COPY chal.py .
COPY flag.txt .
COPY run.sh .
COPY supervisord.conf .

# 4) Normalize line endings & make scripts executable
RUN dos2unix chal.py run.sh \
 && chmod +x chal.py run.sh

# 5) Install Python libs
RUN pip install pycryptodome fpylll

# 6) Expose the CTF port
EXPOSE 1338

# 7) Launch under supervisord
CMD ["supervisord", "-n", "-c", "/opt/app/supervisord.conf"]
