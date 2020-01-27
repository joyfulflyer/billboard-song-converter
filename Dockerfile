FROM python:3.8-slim-buster

RUN pip3 install pipenv

COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock

WORKDIR /app

RUN pipenv sync

COPY ./ /app

ENTRYPOINT [ "pipenv", "run"]
CMD ["python", "start.py" ]
