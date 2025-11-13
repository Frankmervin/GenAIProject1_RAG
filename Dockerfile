FROM python:3.10-slim-buster

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Document the port app listens on
EXPOSE 8080

CMD ["python3","main.py"]