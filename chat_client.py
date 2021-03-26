import threading

import zmq


class ChatClient:
    def __init__(self, username: str, server_host: str, server_port: int, chat_pipe: zmq.Socket):
        self.context = zmq.Context()
        self.username = username
        self.server_host = server_host
        self.server_port = server_port
        self.chat_sock = None
        self.chat_pipe = chat_pipe
        self.poller = zmq.Poller()

    def connect_to_server(self):
        self.chat_sock = self.context.socket(zmq.REQ)
        self.chat_sock.connect(f'tcp://{self.server_host}:{self.server_port}')

    def register_with_poller(self):
        self.poller.register(self.chat_sock, zmq.POLLIN)

    def reconnect_to_server(self):
        self.poller.unregister(self.chat_sock)
        self.chat_sock.setsockopt(zmq.LINGER, 0)
        self.chat_sock.close()
        self.connect_to_server()
        self.register_with_poller()

    def prompt_for_message(self):
        return self.chat_pipe.recv_string()

    def send_message(self, message):
        self.chat_sock.send_json({'username': self.username, 'message': message})

    def get_reply(self):
        self.chat_sock.recv()

    def has_message(self):
        events = dict(self.poller.poll(3000))
        return events.get(self.chat_sock) == zmq.POLLIN

    def run(self):
        self.connect_to_server()
        self.register_with_poller()

        while True:
            message = self.prompt_for_message()
            self.send_message(message)
            if self.has_message():
                self.get_reply()
            else:
                self.reconnect_to_server()

    def run_concurrent(self) -> threading.Thread:
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
        return thread
