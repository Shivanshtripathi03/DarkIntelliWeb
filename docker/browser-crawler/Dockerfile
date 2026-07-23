FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install firefox

COPY . .

ENV PYTHONPATH=/app
CMD ["python", "crawler/browser_worker.py"]
