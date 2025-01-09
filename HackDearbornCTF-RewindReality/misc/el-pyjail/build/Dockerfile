FROM python:latest

RUN apt update -y && \
    apt upgrade -y && apt install socat -y

WORKDIR /app
COPY jail.py flag.txt /app/
RUN mv /app/flag.txt /app/.flag && \
    echo "-a" >> hint.txt

EXPOSE 1337
ENTRYPOINT ["socat", "TCP-LISTEN:1337,reuseaddr,fork","EXEC:\"python3 /app/jail.py\""]