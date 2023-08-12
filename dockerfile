FROM python:3.8.15

USER root

COPY app.py app.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENV DB_URL mongodb://mongo:27017

EXPOSE 9527

ENTRYPOINT ["python", "app.py"]
