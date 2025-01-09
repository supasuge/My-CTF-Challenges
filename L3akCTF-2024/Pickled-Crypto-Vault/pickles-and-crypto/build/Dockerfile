FROM python:3.11-alpine as build

# Create and set the working directory
WORKDIR /app
# Add CTF user
RUN adduser -D -g '' ctfuser
# change the owner of the working directory to ctfuser
RUN chown -R ctfuser /app

USER ctfuser

COPY --chown=ctfuser:ctfuser requirements.txt app.py flag.txt /app/

RUN pip install --no-cache-dir -r requirements.txt && \
    chmod 444 /app/flag.txt && \
    chmod 444 /app/app.py && \
    chattr +i /app/flag.txt && \
    chattr +i /app/app.py && \ 
    chattr +i /app/requirements.txt
EXPOSE 5000
ENV FLASK_APP=app.py


CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
