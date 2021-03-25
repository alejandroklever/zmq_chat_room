import zmq

context = zmq.Context()

print("Connecting to hello world server…")
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:5555")


try:
    while True:
        s = input()
        socket.send(s.encode('utf-8'))
except KeyboardInterrupt:
    pass
