FROM python:3.7-slim
# FROM gcr.io/google-appengine/python


# Use -p python3 or -p python3.7 to select python version. Default is version 2.
# RUN virtualenv /env -p python3

# Setting these environment variables are the same as running
# source /env/bin/activate.
# ENV VIRTUAL_ENV /env
# ENV PATH /env/bin:$PATH

# Copy the application's requirements.txt and run pip to install all
# dependencies into the virtualenv.
# ADD requirements.txt /app/requirements.txt
# ADD .env .env
ADD . .
RUN pip install -r requirements.txt

ARG _BASE_URL
ENV _BASE_URL $_BASE_URL

ARG _AIRTABLE_API_KEY
ENV _AIRTABLE_API_KEY $_AIRTABLE_API_KEY

ARG _AIRTABLE_BASE_ID
ENV _AIRTABLE_BASE_ID $_AIRTABLE_BASE_ID

CMD [ "python", "-u", "./main.py" ]