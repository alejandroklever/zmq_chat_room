
import zmq



context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:5555")

users = {}

try:
    while True:
        message = socket.recv()
        print(message.decode('utf-8'))
        socket.send(b"1")
except InterruptedError:
    pass
