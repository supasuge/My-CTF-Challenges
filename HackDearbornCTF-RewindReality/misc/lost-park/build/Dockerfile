FROM python:3.12-slim

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y socat supervisor && apt-get autoremove -y && apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    useradd -ms /bin/bash hd3

WORKDIR /app
COPY supervisord.conf /app/supervisord.conf
COPY serv.py /app/serv.py

RUN chown -R hd3:hd3 /app && \
    chmod -R 755 /app

EXPOSE 9423

USER hd3

CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]