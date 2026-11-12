# Stage 1: install Python dependencies
FROM python:3.12-slim AS builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install/deps -r requirements.txt


# Stage 2: final runtime image
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy only installed dependencies from Stage 1
COPY --from=builder /install/deps /usr/local

# Copy only the application file needed at runtime
COPY app.py .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["python", "app.py"]