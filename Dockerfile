FROM alpine:latest
LABEL MAINTAINER="https://github.com/htr-tech/zphisher"
WORKDIR /zphisher/
ADD . /zphisher
RUN apk add --no-cache python3 bash ncurses curl unzip wget php 
CMD ["python3", "zphisher.py"]
