FROM python:3.12-alpine AS builder
ENV PYTHONBUFFERED=1
USER root
RUN apk add --no-cache supervisor && \
    adduser -D -g '' dctf3
    
RUN mkdir -p /var/log/supervisor && \
    chown -R dctf3:dctf3 /var/log/supervisor && \
    rm -f /etc/supervisord.conf 
COPY supervisord.conf /etc/supervisord.conf
WORKDIR /app
RUN chown -R dctf3:dctf3 /app

USER dctf3

COPY --chown=dctf3:dctf3 requirements.txt app.py flag.txt chat.py .env /app/
COPY --chown=dctf3:dctf3 static /app/static
# These permissions are so that no one is able to make modification's to vital system resources for running the challenge... 
# It's trivial to get a reverse shell in this challenge
RUN pip install --user -r requirements.txt --no-cache-dir && \
    chmod 555 /app/app.py && \
    chmod 440 /app/.env && \
    chmod 555 /app/chat.py && \
    chmod 444 /app/static/index.html && \
    chmod 444 /app/static/bg.webp && \
    chmod 444 /app/flag.txt && \
    chattr +i /app/.env && \
    chattr +i /app/flag.txt && \
    chattr +i /app/app.py && \
    chattr +i /app/chat.py  && \
    chattr +i /app/static/index.html && \
    chattr +i /app/static/bg.webp

EXPOSE 5000

CMD ["/usr/bin/supervisord"]
