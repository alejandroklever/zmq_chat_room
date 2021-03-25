import time
import zmq
import dataclasses
from typing import List

from zmq.sugar import context



@dataclasses.dataclass
class User:
    username: str
    address: str
    port: str


@dataclasses.dataclass
class Message:
    username: str
    text: str


class ChatServer:
    messages: List[Message]

    def __init__(self, port: int = 8888):
        self.context: zmq.Context = zmq.Context()
        self.port: int = port
        self.socket: zmq.Socket = self.context.socket(zmq.PAIR)
        self.socket.bind(f"tcp://*:{port}")

    def run(self):
        while True:
            data = self.socket.recv_json()
            username = data['username']
            message = data['message']
