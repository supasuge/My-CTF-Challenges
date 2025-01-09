FROM python:3.11-slim-bullseye  


WORKDIR /app

COPY server.py ans.txt flag.txt /app/

ENV SERVER_HOST 0.0.0.0
ENV SERVER_PORT 9999
EXPOSE 9999

CMD ["python", "./server.py"]


# Buidl the docker image
# docker built -t quiz-challenge .
# docker run --name quiz-challenge -p 9999:9999 -d quiz-challenge

# Viewing the logs
# docker logs quiz-challenge-container
