FROM python:3.8.19-alpine3.20

RUN apk update
RUN apk add --no-cache gcc build-base

RUN pip3 install -U pip
ADD requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

RUN mkdir -p /app
ADD ./src/ /app/
ADD ./docker/x-run.sh /

ENV PYTHONPATH /app

ARG PORT=8099
RUN echo $PORT
ENV PORT $PORT

CMD /bin/sh x-run.sh $PORT
