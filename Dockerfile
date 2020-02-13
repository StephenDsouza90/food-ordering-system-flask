FROM ubuntu:18.04

RUN mkdir /app
WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip python3.7
RUN pip3 install Flask waitress SQLALchemy

ADD main.py server.py core.py models.py constants.py /app/

EXPOSE 8080

CMD ["python3", "server.py"]
