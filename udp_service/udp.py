import globals
import socket
import threading
import json

class UDPService(object):

    # configuration
    ip_addr = '127.0.0.1'
    listenport = 1805
    sendport = 1806
    thread = None

    def __init__(self):
        """
        Sets up UDP/IBUS bridge endpoint
        """
        print "UDP target IP: ", self.ip_addr
        print "UDP listen port: ", self.listenport
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip_addr, self.listenport))
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = True
        self.thread.start()

    def start(self):
        """
        Starts listen service
        """
        while True:
            data, addr = self.sock.recvfrom(1024)
            if len(data) > 0:
                self.process_dgram(data, addr)

    def destroy(self):
        """
        Closes socket
        """
        try:
            print "Destroying UDP service..."
            self.sock.close()
        except (TypeError, Exception):
            pass

        self.sock = None
        self.thread = None

    def process_dgram(self, data, addr):
        checksum = 0
        for el in data:
            checksum ^= ord(el)
            
        if globals.debug:
            print >>globals.ibus_log, addr, "udp_rx: " + data.encode("hex") + " cs: " + hex(checksum)
        
        globals.ibus_service.write_to_ibus(data + chr(checksum))

    def send_packets_to_udp(self, ibus_packets):
        try:
            print >>globals.ibus_log, "Sending encapsulated IBUSPacket(s)..."
            for ibus_packet in ibus_packets:
                if globals.debug:
                    print >>globals.ibus_log, ibus_packet
                self.sock.sendto(ibus_packet.raw, (self.ip_addr, self.sendport))

            return True

        except Exception as e:
            # socket was closed, graceful restart
            print "Error: " + e.message
            globals.restart_udp()
            return False

