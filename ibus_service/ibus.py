#!/usr/bin/env python
import sys
sys.path.append("/storage/python") # FIXME configurable module path
import serial
import globals
from packet import IBUSPacket
import threading
import time

class IBUSService(object):

    # configuration
    baudrate = 9600
    handle = None
    parity = serial.PARITY_EVEN
    port = '/dev/ttyUSB0'
    timeout = 1
    thread = None

    def __init__(self):
        """
        Initializes bi-directional communication with IBUS adapter via USB
        """
        self.handle = serial.Serial(self.port, parity=self.parity, timeout=self.timeout, stopbits=1)
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = True
        self.thread.start()

    def start(self):
        """
        Starts listen service
        """
        while True:
            data = self.handle.read(9999)
            if len(data) > 0:
                self.process_bus_dump(data)

    def destroy(self):
        """
        Closes serial connection and resets handle
        """
        try:
            print "Destroying IBUS service..."
            self.handle.close()
        except (TypeError, Exception):
            pass

        self.handle = None
        self.thread = None

    def process_bus_dump(self, dump, index=0):
        """
        Processes bytes received from serial and parse packets

        ---------------------------------------------
        | Source ID | Length | Dest Id | Data | XOR |
        ---------------------------------------------
                             | ------ Length -------|

        """
        packets = []
        hex_dump = dump.encode('hex')
        if globals.debug:
            print >>globals.ibus_log, time.asctime(time.localtime()) + " IBUS RX: " + hex_dump

        while index < len(hex_dump):
            try:
                # construct packet while reading
                current_packet = ""

                # extract source id
                source_id = hex_dump[index:(index+2)]
                current_packet += source_id
                index += 2

                # extract length info
                length = hex_dump[index:(index+2)]
                current_packet += length
                total_length_data = int(length, 16)
                total_length_hex_chars = (total_length_data * 2) - 4
                index += 2

                # extract destination id
                destination_id = hex_dump[index:(index+2)]
                current_packet += destination_id
                index += 2

                # extract inner data
                data = hex_dump[index:(index+total_length_hex_chars)]
                current_packet += data
                index += total_length_hex_chars

                # extract xor checksum
                xor = hex_dump[index:(index+2)]
                current_packet += xor
                index += 2

                # confirm full packet exists
                expected_packet_length = (2 + 2 + 2 + total_length_hex_chars + 2)
                if current_packet.__len__() != expected_packet_length:
                    continue

                # create packet
                packet = IBUSPacket(source_id=source_id, length=total_length_data, destination_id=destination_id,
                                    data=data, xor_checksum=xor, raw=current_packet)

                # add packet if valid
                if packet.is_valid():
                    packets.append(packet)

            except Exception as e:
                print "Error processing bus dump: " + e.message

        # process packets data (and send to Android)
        self.process_packets(packets)

    @staticmethod
    def process_packets(packets):
        """
        Process packets [] and send to UDP (if service is active)
        """
        if globals.udp_service is not None:
            try:
                globals.udp_service.send_packets_to_udp(packets)
            except Exception as e:
                print "Error: " + e.message + "\nFailed to send packets to udp"
                return False

        return True

    def write_to_ibus(self, data):
        """
        Writes the provided data to the bus
        """
        try:
            self.handle.write(data)
        except Exception as e:
            print "Cannot write to IBUS: " + e.message
            globals.restart_services()
