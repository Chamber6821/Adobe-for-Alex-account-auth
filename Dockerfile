FROM seleniarm/standalone-chromium:121.0

USER root

RUN apt-get update && apt-get install -y python3.11 python3.11-venv python3-pip \
    && python3.11 -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

ENV PYTHONPATH=/app

CMD ["/app/venv/bin/python3", "app/main.py"]
