FROM python:3.7-slim
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt