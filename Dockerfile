FROM python:3.11-slim

WORKDIR /app

COPY src ./src

RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r src/requirements.txt

CMD ["python", "src/main.py"]
