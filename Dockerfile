FROM seleniarm/standalone-chromium:latest

USER root

RUN apt-get update && apt-get install -y python3-pip python3-venv \
    && python3 -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

COPY account-auth /app/

ENV PYTHONPATH=/app

CMD ["/app/venv/bin/python3", "app/main.py"]
