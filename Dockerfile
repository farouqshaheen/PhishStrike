FROM python:3.11-slim
LABEL MAINTAINER="https://github.com/farouqshaheen/PhishStrike"

RUN apt-get update && apt-get install -y --no-install-recommends php && rm -rf /var/lib/apt/lists/*

WORKDIR /phishstrike/
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /phishstrike/

# Override at runtime: -e SECRET_KEY=... -e ADMIN_PASSWORD=...
ENV DASHBOARD_HOST=127.0.0.1 \
    DASHBOARD_RUNTIME=socketio \
    CAPTURE_ENCRYPT=false \
    RETENTION_DAYS=0

CMD ["python3", "-m", "phishstrike"]
