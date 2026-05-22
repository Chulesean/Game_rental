FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml /app/
COPY code/ /app/code/

# Install Python dependencies
RUN pip install --no-cache-dir \
    flask>=3.0 \
    flask-sqlalchemy>=3.1 \
    flask-login>=0.6 \
    flask-wtf>=1.2 \
    psycopg2-binary>=2.9 \
    gunicorn>=21.2 \
    python-dotenv>=1.0

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "/app/code", "flask_app:create_app()"]
