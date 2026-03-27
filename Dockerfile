FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY labeldesk ./labeldesk

RUN uv sync --frozen --no-dev

ENV LABELDESK_HOME=/data
ENV LABELDESK_DEFAULT_WEB_HOST=0.0.0.0
VOLUME /data

EXPOSE 7432

ENTRYPOINT ["uv", "run", "labeldesk"]
CMD ["web", "--api-only"]
