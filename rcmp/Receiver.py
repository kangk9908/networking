# 3 Nov 2021
# CS-332 Reliable File Transfer Client
# Prof. Norman
# Created by: Kun Kang (kk58) & Ifeanyi Onyeanakwe (iko2)

import socket
import argparse
import random

parser = argparse.ArgumentParser(description="A prattle server")

parser.add_argument("-n", "--name", dest="name",
                    help="name to be prepended in messages (default: machine name)")
parser.add_argument("-s", "--server", dest="server", default="127.0.0.1",
                    help="server hostname or IP address (default: 127.0.0.1)")
parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                    help="TCP port the server is listening on (default 12345)")
parser.add_argument("-f", "--filename", dest="file_name", type=str,
                    help="NAME OF FILE")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                    help="turn verbose output on")
args = parser.parse_args()
file_name = args.file_name


UDP_IP = ""
UDP_PORT = args.port
PACKET_LENGTH = 1463
PACKET_BODY_LENGTH = 1450
DATA_START_OFFSET = 13

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

# https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
# write binary
fin = open(file_name, "wb")

# set the values that help control the file operations and packet sending
file_size = -1
packet_count = -1
bytes_remainder = -1
previous_packet_ID = -1

while(True):
    data, addr = sock.recvfrom(PACKET_LENGTH)
    # sock.settimeout(1)

    if data:
        # set the connectionID as the data part 0 - 4
        connectionID_Bytes = data[0:4]
        connectionID = int.from_bytes(connectionID_Bytes, 'big')

        # set the packet ID as the data part 8 - 12
        packet_ID_Bytes = data[8:12]
        packet_ID = int.from_bytes(packet_ID_Bytes, 'big')

        # Next packet to be ACKed
        should_ack = data[12]

        print("Received data:- ConnectionID: " + str(connectionID) + " packetID: " +
              str(packet_ID) + " and next ACK value: " + str(should_ack))

        # check if file size is -1 because we only want to do this once
        if file_size == -1:
            file_size = int.from_bytes(data[4:8], 'big')
            packet_count = file_size // PACKET_BODY_LENGTH
            bytes_remainder = file_size % PACKET_BODY_LENGTH
            if bytes_remainder > 0:
                packet_count += 1

        data_size = 0
        if int.from_bytes(packet_ID_Bytes, 'big') == packet_count - 1 and bytes_remainder > 0:
            data_size = bytes_remainder
        else:
            data_size = PACKET_BODY_LENGTH

        # check if packet contains correct data (ie packet is the current packet to be sent)
        if packet_ID == previous_packet_ID + 1:
            fin.seek(packet_ID * PACKET_BODY_LENGTH)
            data = data[DATA_START_OFFSET:DATA_START_OFFSET + data_size]
            fin.write(data)
        # check if packet is behind schedule
        elif packet_ID <= previous_packet_ID:
            pass

        # check if packet is ahead of schedule then drop
        elif packet_ID > previous_packet_ID + 1:
            continue

        # create random int to establish unreliability
        rando = random.randint(0, 1)

        # ACKS only when the unreliability allows it
        if should_ack == 1 and rando == 1:
            # Sends a confirmatory ACK to the sender after data receipt
            ack_data = connectionID_Bytes + packet_ID_Bytes
            sent = sock.sendto(ack_data, addr)

            print("Sent ACK of " + str(sent) + " bytes back to " + str(addr) + " with PacketID : "
                  + str(int.from_bytes(packet_ID_Bytes, 'big')) + " and data size: " + str(data_size))

        # Exit if the last packet is sent
        if packet_count - 1 == packet_ID:
            print("File Transfer Completed")
            print("Exiting...")
            break
        previous_packet_ID = packet_ID

fin.close()
sock.close()
