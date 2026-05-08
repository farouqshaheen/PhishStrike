FROM alpine:latest
LABEL MAINTAINER="https://github.com/farouqshaheen/PhishStrike"
WORKDIR /phishstrike/
ADD . /phishstrike
RUN apk add --no-cache python3 bash ncurses curl unzip wget php 
CMD ["python3", "phishstrike.py"]
