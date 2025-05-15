FROM python:3.12-slim

WORKDIR /app
COPY requirements-service.txt .
RUN pip install --no-cache-dir -r requirements-service.txt

COPY transcriber_service.py . 
COPY .env . 

# Expose
EXPOSE 8000
CMD ["uvicorn", "transcriber_service:app", "--host", "0.0.0.0", "--port", "8000"]
