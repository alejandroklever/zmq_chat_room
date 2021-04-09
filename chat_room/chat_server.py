import dataclasses
from typing import List, Tuple

import zmq


@dataclasses.dataclass
class Message:
    username: str
    text: str

    @staticmethod
    def from_json(data):
        return Message(data['username'], data['message'])

    def to_json(self):
        return {'username': self.username, 'message': self.text}


class ChatServer:
    messages: List[Message] = []

    def __init__(self, host: str, port: int, screen_host: str, screen_port: int):
        self.context = zmq.Context()
        self.host = host
        self.port = port
        self.screen_host = screen_host
        self.screen_port = screen_port

    def bind(self) -> Tuple[zmq.Socket, zmq.Socket]:
        # binding process
        socket = self.context.socket(zmq.REP)
        socket.bind(f'tcp://{self.host}:{self.port}')

        screen_socket = self.context.socket(zmq.PUB)
        screen_socket.bind(f'tcp://{self.screen_host}:{self.screen_port}') 
        
        return socket, screen_socket

    def run(self):
        socket, screen_socket = self.bind()

        while True:
            data = socket.recv_json()
            self.messages.append(Message.from_json(data))
            socket.send(b'\x00')
            screen_socket.send_json(data)
