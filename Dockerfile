FROM python:3.11-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY ./ /usr/src/app
WORKDIR /usr/src/app

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]
