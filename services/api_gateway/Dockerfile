# Use a slim Python image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
ENV PORT=8000

# Set the working directory
WORKDIR $APP_HOME

# Install curl for healthcheck and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app.py .
COPY health.py .

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application using Gunicorn with Uvicorn workers (production setup)
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app:app"]

# Health check
HEALTHCHECK --interval=15s --timeout=2s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/live || exit 1

