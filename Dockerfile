FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 👇 Denne skal være EFTER den ovenfor, så den overskriver root/index.html
COPY frontend/ /app/

EXPOSE 8000

CMD ["uvicorn", "chatbot:app", "--host", "0.0.0.0", "--port", "8000"]



