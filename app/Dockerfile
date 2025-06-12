FROM python:3.12-slim

WORKDIR /app
COPY . /app/

# Install system dependencies if needed (optional, depends on your packages)
# RUN apt-get update && apt-get install -y build-essential

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Also install specific packages (if you want to keep these explicitly)
RUN pip install --no-cache-dir fastapi uvicorn jinja2

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
