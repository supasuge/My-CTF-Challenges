FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y --no-install-recommends supervisor && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


WORKDIR /app
COPY requirements.txt /app/
COPY app.py /app/
COPY flag.txt /app/
COPY templates/ /app/templates/
RUN pip install -r requirements.txt --no-cache-dir

COPY supervisord.conf /app/supervisord.conf

EXPOSE 9898

CMD [ "/usr/bin/supervisord", "-c", "/app/supervisord.conf"]


