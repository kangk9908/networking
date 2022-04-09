#############################
# CS332 - Prof. Norman      #
# 20 September 2021         #
# Kun Kang                  #
# TCP Chat Client           #
#############################

# general reference
# https://www.geeksforgeeks.org/simple-chat-room-using-python/
import select, socket, sys, argparse
from threading import Thread

# https://www.tutorialspoint.com/python-program-to-find-the-ip-address-of-the-client
# getting host name and IP address
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                # establishing socket

#  /home/cs/332/fa2021/chat/talk_client_skeleton.py
parser = argparse.ArgumentParser(description="A prattle client")

parser.add_argument("-n", "--name", dest="name", help="name to be prepended in messages (default: machine name)")
parser.add_argument("-s", "--server", dest="server", default="127.0.0.1",
                    help="server hostname or IP address (default: 127.0.0.1)")
parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                    help="TCP port the server is listening on (default 12345)")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                    help="turn verbose output on")
args = parser.parse_args()

# https://realpython.com/python-sockets/#tcp-sockets
# https://docs.python.org/3/howto/sockets.html
userName = args.name                                                                    # get username from -n            
server = args.server                                                                    # get server from -s
port = int(args.port)                                                                   # get port from -p
sock.connect((server, port))                                                            # connect server and port to socket
while not userName:                                                                     # if userName is not given through -n
    userName = input("Please input name : ")                                            # asks for userName

# https://www.geeksforgeeks.org/python-strings-decode-method/
data = sock.recv(2048)                                                                  # recieve message from server
print(data.decode())                                                                    # print out the decoded message "Thank you for connecting"
sock.send((userName + " has connected to the server!").encode())

def wait_for_message():                                                                 # create defintion for wait for message
    while True:
        message = sock.recv(2048).decode()                                              # recieve message and decode
        if not message:                                                                 # if server connection lost unexpectedly print message     
            print("The server connection has been lost. Please press 'ctrl-c'.")
            sock.close()
            quit()                                                                  
        else:
            print(message + "\n")

def send_goodbye_msg():
    sock.send((userName + " has disconnected from the party").encode())

# https://www.thepythoncode.com/article/make-a-chat-room-application-in-python
# used for reference only on how to use threads            
wait4msg = Thread(target=wait_for_message)                                              # create a thread for def wait for message
wait4msg.daemon = True                                                                  # daemon thread
wait4msg.start()                                                                        # start

# https://stackoverflow.com/questions/27260751/python-hide-c-from-sigint
# https://www.programiz.com/python-programming/exception-handling
while True:
    try:
        sock.send((userName + " says : " + input('\n')).encode())                      # send encoded message
    except KeyboardInterrupt:                                                          # keyboard interrupt exception
        print("\b\b\r-------------------")                                             # deletes the "^C" in terminal when you use keyboard interrupt
        print("Exited service. Goodbye. Hope to see you again.")
        send_goodbye_msg()
        quit()
    except RuntimeError:                                                               # runtime error exception
        print("Disconnected from the server.")
        send_goodbye_msg()
        quit()
