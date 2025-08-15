# ===== Builder =====
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# bring in requirements and prebuild wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ===== Runtime =====
FROM python:3.12-slim

# non-root user
RUN useradd -m appuser

# minimal OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install deps from prebuilt wheels (two safe options; pick ONE)

# Option A: install only .whl files
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl

# Option B (preferred if you use markers/extras): keep resolver but offline
# COPY --from=builder /wheels /wheels
# COPY requirements.txt .
# RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# copy app source
COPY . /app

ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    UPLOAD_FOLDER=/app/uploaded_files \
    PORT=8000

RUN mkdir -p /app/uploaded_files && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "60", "app:app"]
