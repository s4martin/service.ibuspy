import socket
import argparse

parser = argparse.ArgumentParser(description="Send a message to the IBUS")
parser.add_argument('--ip', default="127.0.0.1")
parser.add_argument('--port', type=int, default=1805)
parser.add_argument('message', metavar='N', nargs='?')
parser.add_argument('--button', nargs='?', choices=['power', 'mode'], help="Button press to send")

args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (args.ip, args.port)

hex_data = ""
if (args.message):
    hex_data = args.message
else:
    if args.button != None:
        if args.button == "power":
            hex_data = 'f004684806'
        elif args.button == "mode":
            hex_data = 'f004684823'

if hex_data != "":
    print "Sending datagram to ", dest, " : ", hex_data
    sock.sendto(hex_data.decode('hex'), dest)
else:
    print "No data to send"     
