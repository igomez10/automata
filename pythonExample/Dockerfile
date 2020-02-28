FROM python:3.7-alpine
ADD . /app
RUN python -m http.server $PORT &
CMD [ "python", "-u", "./app/main.py" ]
