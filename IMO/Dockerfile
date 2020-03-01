FROM python:3.7-slim
ADD . .

ARG _BASE_URL
ENV _BASE_URL $_BASE_URL

RUN pip install -r requirements.txt
CMD [ "python", "-u", "./main.py" ]
