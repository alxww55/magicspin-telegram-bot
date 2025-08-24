FROM python:3.13.7-alpine
WORKDIR /usr/local/magicspin_bot
COPY ["requirements.txt", ".env", "main.py", "./"]
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN adduser -D magicspin_bot