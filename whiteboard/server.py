#
# Websocket-based server code. This code sends to other clients whatever
# each client sends to it. Thus, this is essentially a broadcasting service.
#
# Date: 24 June 2021
# Original author: Victor Norman at Calvin University
# Editted by Kun Kang

import asyncio
import websockets
import json
import socket

from websockets import client

# Change to False when you are done debugging.
DEBUG = False
# Port the server listens on to receive connections.
PORT = 8001

client_id = 0

# TODO: need a variable here to hold all connected clients' websocket objects.  done
connected_clients = []

# create new class for Client
class Client:
    id = 0
    ws = None

    def __init__(self, sock, ID):
        self.ws = sock
        self.id = ID

    def get_id(self):
        return self.id
    
    def get_socket(self):
        return self.ws

def register_new_client(client_ws):
    if DEBUG:
        print('register new client!')
    # TODO: add code here to store the client_ws in your collection of websockets. done
    global client_id

    # added client to clients array
    connected_clients.append(client_ws)

    # in case the first client ever disconnects preventing the transfer of data to other clients
    client_id += 1


def unregister_client(websocket):
    if DEBUG:
        print('removed new client!')
    # TODO: add code here to remove the client_ws from your collection of websockets.   done
    connected_clients.remove(websocket)


async def per_client_handler(client_ws, path):
    '''This function is called whenever a client connects to the server. It
    does not exit until the client ends the connection. Thus, an instance of
    this function runs for each connected client.'''
    global client_id
    myClient = Client(client_ws, client_id)
    register_new_client(myClient)
    try:
        async for message in myClient.ws:
            # This next line assumes that the message we received is a stringify-ed
            # JSON object.  data will be a dictionary.
            data = json.loads(message)
            print('got data ', data)

            # TODO: Add the client's unique id to the message before        done
            # sending to everyone.
            data['id'] = myClient.get_id()


            # TODO: Send received message to all *other* clients.
            for client in connected_clients:
                if not client.get_id() == myClient.get_id():
                    await client.get_socket().send(json.dumps(data))


    finally:
        unregister_client(client_ws)


# Adapted from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def getNetworkIp():
    '''This is just a way to get the IP address of interface this program is
    communicating over.'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


# Run websocket server on port PORT on the local loopback interface while you are
# still debugging your own code.
start_server = websockets.serve(per_client_handler, "localhost", PORT)
# TODO: use this next line when you are ready to deploy and test your code with others.
# (And comment out the line above.)
# start_server = websockets.serve(per_client_handler, getNetworkIp(), PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


# What would you have to change in the protocol if you wanted to allow a user to:
# erase areas
'''If I wanted to allow the user to erase, I would implement an option to set the color to NULL or -1'''

# write text
'''I am not sure how this would work but if I could I would try to implement a text box and allow the user
to choose between the whiteboard and text box. For the text box I would just establish a connection like I did
in the client and server chat'''

# take (and release) control of the whiteboard.
'''I would give each client an unique ID and make the first client have control of the whitebaord. When that
client disconnects, the next client would have control.'''
