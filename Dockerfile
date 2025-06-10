FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 👇 Denne linje sørger for at frontend-filerne overskrives korrekt i containeren
RUN cp -r /app/frontend/* /app/frontend/

CMD ["uvicorn", "chatbot:app", "--host", "0.0.0.0", "--port", "8000"]


