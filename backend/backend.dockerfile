FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements if available
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose FastAPI default port
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8080"]