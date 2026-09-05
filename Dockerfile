FROM python:3.13.3-slim-bookworm

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 4000

# Run with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:4000", "app:app"]