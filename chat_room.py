import argparse
import configparser
import curses
import threading
import time
from curses import wrapper


import zmq
import typer

from chat_client import ChatClient
from chat_screen import ChatScreen
from chat_server import ChatServer


app = typer.Typer()


def screen_recv(display):
    while True:
        # alternate color pair used to visually check how frequently this loop runs
        # to tell when user input is blocking
        print(display.recv_string())

def screen_send(chat_sender):
    while True:
        s = input()
        if s is not None and s != "":
            chat_sender.send_string(s)
        # need to do sleep here...
        # if bottom window gets down to `window.getstr...` while top window is setting up,
        # it registers a bunch of control characters as the user's input
        time.sleep(0.005)


@app.command()
def serve(host: str = '*', port: int=8888, screen_host: str = '*', screen_port: int = 8889):                            
    server = ChatServer(host, port, screen_host, screen_port)
    try:
        server.run()
    except KeyboardInterrupt:
        pass

@app.command()
def connect(username: str, host: str = 'localhost', port: int=8888, screen_port: int = 8889):
    # Create a pipe for de io comunication
    receiver = zmq.Context().instance().socket(zmq.PAIR)
    receiver.bind("inproc://clientchat")

    sender = zmq.Context().instance().socket(zmq.PAIR)
    sender.connect("inproc://clientchat")
    
    client = ChatClient(username, host, port, receiver)
    client.run_concurrent()

    display_receiver = zmq.Context().instance().socket(zmq.PAIR)
    display_receiver.bind("inproc://clientdisplay")
    
    display_sender = zmq.Context().instance().socket(zmq.PAIR)
    display_sender.connect("inproc://clientdisplay")
    
    display = ChatScreen(host, screen_port, display_sender)
    display.run_concurrent()


    screen_recv_thread = threading.Thread(target=screen_recv, args=(display_receiver,))
    screen_recv_thread.daemon = True
    screen_recv_thread.start()

    screen_send_thread = threading.Thread(target=screen_send, args=(sender,))
    screen_send_thread.daemon = True
    screen_send_thread.start()

    
    screen_recv_thread.join()
    screen_send_thread.join()


if '__main__' == __name__:
    try:
        app()
    except KeyboardInterrupt as e:
        pass
    except:
        raise
