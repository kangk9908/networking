#############################
# CS332 - Prof. Norman      #
# 28 September 2021         #
# Kun Kang                  #
# TCP Chat Server           #
#############################
import socket
import select
import argparse

parser = argparse.ArgumentParser(description="A prattle server")

parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                    help="TCP port the server is listening on (default 12345)")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                    help="turn verbose output on")
args = parser.parse_args()

# https://www.tutorialspoint.com/python-program-to-find-the-ip-address-of-the-client
# getting host name and IP address
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                # establishing socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                              # establishing socket type

port = int(args.port)                                                                   # get port from -p
verbose = bool(args.verbose)                                                            # if verbose ("-v") is called
try:
    sock.bind(("", port))                                                               # binds server to ip(is empty string so that server is accessible from any computer)
except OSError:                                                                         # for when more than one server tries to access same port
    print("Port " + str(port) + " is occupied.")
    exit()
except OverflowError:                                                                   # for when 
    print("Port range exceeded")
    exit()

sock.listen()                                                                           # server listens to connections

sockList = [sock]                                                                       # list of sockets from which to read from


#osError is for when the port is already being used

# https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
# https://towardsdatascience.com/append-in-python-41c37453400
def send_to_socket(socket, message):                                                    # function for sending a message to the server
    try:
        socket.send(message)
    except:
        print("Error sending message from " + str(socket.getpeername()))

# https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
try:
    while True:
        readSockets, _, exceptionSock = select.select(sockList, sockList, sockList)                     # select() chooses which socket to read from
        # for when a connection is made
        for read_from_sock in readSockets:
            
            if read_from_sock == sock:
                client_socket, client_address = sock.accept()                                           
                sockList.append(client_socket)                                                          # adds the client socket to the end of the list
                send_to_socket(client_socket, b"Thank you for connecting to the chat server")           # sends message confirming connection
            
            else:
                message = ''                                                                            # an empty message variable to make sure it is in the correct scope
                
                try:
                    message = read_from_sock.recv(2048)                                                 # receive message
                
                except:
                    print("Unable to receive message from " + str(read_from_sock.getpeername()))        # can't receive message
                
                if not message:                                                                         # remove bad message from socket list
                    sockList.remove(read_from_sock)
                    continue
                
                if verbose == True:                                                                     # if verbose is called
                    print("Received message from " + str(read_from_sock.getpeername()) + " : \""+ message.decode() + "\"")
                
                for recieving_sock in sockList:
                    
                    if recieving_sock == sock or recieving_sock == read_from_sock:
                        continue
                    
                    else:
                        recieving_sock.send(message)

except KeyboardInterrupt:
    print("\b\b\r-------------------")                                                  # deletes the "^C" in terminal when you use keyboard interrupt
    print("Exited service. Goodbye. Hope to see you again.")
    quit()

