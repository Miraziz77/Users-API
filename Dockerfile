# ── Stage 1: install dependencies ──────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime image ─────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Create a non-root user to run the application.
# Running as root inside a container is a security risk.
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy only installed packages from the builder stage — no pip, no cache.
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code.
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic.ini ./alembic.ini

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]