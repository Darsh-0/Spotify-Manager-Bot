FROM python:3.11-slim

WORKDIR /app

# Good defaults
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# If your keep_alive server listens on a port (commonly 8080)
EXPOSE 8080

CMD ["python", "main.py"]
