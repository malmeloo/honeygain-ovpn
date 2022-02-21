FROM alpine

# install python
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 \
    && python3 -m ensurepip \
    && pip3 install -U pip setuptools

# init environment
RUN mkdir app
# COPY manager.py app/
COPY requirements.txt app/
WORKDIR app

RUN pip3 install -U -r requirements.txt

ENTRYPOINT ["/usr/bin/python3", "manager.py"]