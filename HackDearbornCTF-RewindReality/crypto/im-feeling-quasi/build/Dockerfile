FROM python:3.12-slim AS builder


RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y python3-pip libssl-dev libffi-dev python3-dev socat supervisor && \
    apt-get autoremove -y && \
    apt-get clean -y

WORKDIR /app

COPY chal.py .
COPY flag.txt .
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 1337

# Start socat to listen on port 1337 and run chal.py

CMD ["/usr/bin/supervisord"]