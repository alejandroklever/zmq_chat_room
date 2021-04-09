FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN rm -r __pycache__ .idea chat_room/__pycache__


ENTRYPOINT [ "python3", "chat_room" ]
# CMD [ "python3", "chat_room", "serve"]