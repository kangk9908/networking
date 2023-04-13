# 3 Nov 2021
# CS-332 Reliable File Transfer Server
# Prof. Norman
# Created by: Kun Kang (kk58) & Ifeanyi Onyeanakwe (iko2)

import socket
import argparse
import os

parser = argparse.ArgumentParser(description="A prattle server")

parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                    help="TCP port the server is listening on (default 12345)")
parser.add_argument("-f", "--filename", dest="file_name", type=str,
                    help="NAME OF FILE")
parser.add_argument("-s", "--server", dest="server", type=str, default="0.0.0.0",
                    help="IP Address")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                    help="turn verbose output on")
args = parser.parse_args()

file_name = args.file_name

UDP_IP = args.server
UDP_PORT = args.port
PACKET_LENGTH = 1450

packet_ID = int(0)
prev_acked_pkt = -1
gap_counter = 0
acked = 0
unique_ID = os.urandom(4)

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.settimeout(1)

# https://thepythonguru.com/python-how-to-read-and-write-files/
# read binary
fin = open(file_name, "rb")
file_size = os.path.getsize(file_name)

# create variables for the number of packets and the number of bytes remaining to send
packet_count = file_size // PACKET_LENGTH
bytes_remainder = file_size % PACKET_LENGTH

# increment # of packets to send if bytes are left to send
if bytes_remainder > 0:
    packet_count += 1

while(True):
    try:
        if(packet_ID - prev_acked_pkt - 1 == gap_counter):
            acked = 1

        else:
            acked = 0

        # Header that gives info about the packet
        header = unique_ID + \
            file_size.to_bytes(4, 'big') + packet_ID.to_bytes(4,
                                                              'big') + acked.to_bytes(1, 'big')

        # Read data from the file in the byte size specified
        data_size = 0
        if packet_ID == packet_count - 1 and bytes_remainder > 0:
            data_size = bytes_remainder
        else:
            data_size = PACKET_LENGTH
        data = fin.read(data_size)

        print("Sending packet of size: " + str(len(header + data)) + " with packet ID : "
              + str(packet_ID) + " and data size: " + str(data_size))

        try:
            # Send the data to the receiver
            sock.sendto(header + data, (UDP_IP, UDP_PORT))

        except socket.timeout:
            print("Sender Timeout Error: Error sending to receiver!")

        if(acked == 1):
            ack_pkt = []
            recvAddress = None
            try:
                # Wait for an ACK that... ACKnowledges receipt (See what I did there...?) LMAO (Laughing My ACKs Off)
                ack_pkt, recvAddress = sock.recvfrom(8)
            except socket.timeout:
                print("Sender Timeout Error: No ACK received!")

            acked_pkt_ID = int.from_bytes(ack_pkt[4:8], 'big')
            print("ACK of " + str(len(ack_pkt)) + " bytes received from " +
                  str(recvAddress) + " ACKed packet ID of " + str(acked_pkt_ID))

            # Keeps track of packets to be ACKed
            if acked_pkt_ID == packet_ID:
                gap_counter += 1
                prev_acked_pkt = packet_ID
                print("Incremented gap counter is " + str(gap_counter))
                if acked_pkt_ID == packet_count - 1:
                    print("Last ACK received.")
                    break
            
            # in case that wrong ACK received go back to last packet sent
            elif acked_pkt_ID != packet_ID or recvAddress is None:
                packet_ID = prev_acked_pkt + 1
                fin.seek(PACKET_LENGTH * packet_ID)
                gap_counter = 0
                print("Incorrect ACK received.")
                continue
        
        # If packet ID of the last packet is received, exit
        if packet_ID == packet_count - 1:
            print("Last packet received.")
            break

        packet_ID += 1

    except KeyboardInterrupt:
        print("\b\b\r-------------------------")
        print("Aborted file transfer")
        exit()

fin.close()
sock.close()
