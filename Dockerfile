FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 👇 Denne skal være EFTER den ovenfor, så den overskriver root/index.html
COPY frontend/ /app/


