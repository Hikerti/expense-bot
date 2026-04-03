FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./

RUN pip install uv
RUN uv venv && \
    uv pip install -e .

COPY . .

RUN mkdir -p data/backups data/attachments

EXPOSE 8080

CMD ["python", "-m", "src.main"]