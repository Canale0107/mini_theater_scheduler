FROM python:3.12-slim

ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# COPY . .

# CMD ["python", "src/scraping/main.py"]