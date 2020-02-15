# Base image
FROM ubuntu:18.04

# Work directory settings
RUN mkdir /app
WORKDIR /app

# Installations
RUN apt-get update && apt-get install -y python3-pip python3.7
RUN pip3 install Flask waitress SQLALchemy

# Local installations
ADD main.py server.py core.py models.py constants.py /app/

# Expose application port
EXPOSE 8080

# Command to runn app
CMD ["python3", "server.py"]
