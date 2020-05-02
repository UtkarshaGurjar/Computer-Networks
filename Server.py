
# Server code for chat system

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

clients = {}
addresses = {}

HOST = "127.0.0.1"
PORT = 5000
BUFFERSIZE = 1024
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(ADDR)


def accept_incoming_client_conn():
    # Function handling the clients
    while True:
        client, client_address = SOCK.accept()
        print("%s:%s has connected." % client_address)
        client.send("Hello everyone in the CCN Course ChatRoom , please enter your name to start ! ".encode("utf8"))
        client.send("Enter your message and enter press enter!".encode("utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(conn, addr):  # Takes client socket as argument.

    name = conn.recv(BUFFERSIZE).decode("utf8")
    welcome = 'Welcome %s! If you want to quit, press quit button' % name
    conn.send(bytes(welcome, "utf8"))
    msg = "%s from [%s] has joined the chat!" % (name, "{}:{}".format(addr[0], addr[1]))
    broadcast_message(bytes(msg, "utf8"))
    clients[conn] = name
    while True:
        msg = conn.recv(BUFFERSIZE)
        if msg != bytes("#quit", "utf8"):
            broadcast_message(msg, name + ": ")
        else:
            conn.send(bytes("#quit", "utf8"))
            conn.close()
            del clients[conn]
            broadcast_message(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast_message(msg, prefix=""):  # prefix is for name identification.
    # this function will broadcast message to all clients connected
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


if __name__ == "__main__":
    SOCK.listen(5)  # Listens for 5 connections at max.
    print("Chat Server has Started !!")
    print("Waiting for connections !")
    ACCEPT_THREAD = Thread(target=accept_incoming_client_conn)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SOCK.close()