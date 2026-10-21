# Runtime image for the FastAPI app (src.main:app), built for ECS Fargate.
FROM python:3.12-slim

WORKDIR /app

# System deps needed by psycopg (libpq) at build time.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 8000

# No --reload in production; ALB health-checks "/" which renders home.html with no DB call.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
