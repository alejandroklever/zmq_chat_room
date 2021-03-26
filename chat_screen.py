import threading
import zmq


class ChatScreen:
    def __init__(self, server_host: str, server_port: int, display_pipe: zmq.Socket):
        self.context = zmq.Context()
        self.server_host = server_host
        self.server_port = server_port
        self.display_sock = None
        self.display_pipe = display_pipe
        self.poller = zmq.Poller()

    def connect_to_server(self):
        self.display_sock = self.context.socket(zmq.SUB)
        self.display_sock.setsockopt_string(zmq.SUBSCRIBE, '')
        self.display_sock.connect(f'tcp://{self.server_host}:{self.server_port}')
        self.poller.register(self.display_sock, zmq.POLLIN)

    def has_message(self):
        events = self.poller.poll()
        return self.display_sock in events

    def run(self):
        self.connect_to_server()
        while True: 
            data = self.display_sock.recv_json()
            username, message = data['username'], data['message']
            self.display_pipe.send_string(f'{username}: {message}')

    def run_concurrent(self) -> threading.Thread:
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
        return thread
