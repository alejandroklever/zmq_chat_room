import time
import zmq
import dataclasses
from typing import List


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"World")


@dataclasses.dataclass
class Message:
    username: str
    text: str


class ChatServer:
    messages: List[Message]

    def __init__(self, port: int = 8888):
        self.port = port