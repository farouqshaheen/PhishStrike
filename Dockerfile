FROM python:3.10-slim
LABEL MAINTAINER="https://github.com/farouqshaheen/PhishStrike"
WORKDIR /phishstrike/
ADD . /phishstrike
RUN pip install -r requirements.txt
CMD ["python3", "phishstrike.py"]
