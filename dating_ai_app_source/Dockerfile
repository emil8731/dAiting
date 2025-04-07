FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Create data directory
RUN mkdir -p data/profiles data/conversations data/logs

# Run the application
CMD gunicorn --bind 0.0.0.0:8080 web_app:app
