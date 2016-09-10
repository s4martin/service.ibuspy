import globals
import xbmcgui
import xbmc
import socket
import threading

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
        print >>globals.ibus_log, "UDP target IP: ", self.ip_addr
        print >>globals.ibus_log, "UDP listen port: ", self.listenport
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip_addr, self.listenport))
        self.sock.settimeout(None)
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = True
        self.thread.start()

    def start(self):
        """
        Starts listen service
        """
        while self.sock != None:
            try:
                data, addr = self.sock.recvfrom(1024)
                if len(data) > 0:
                    self.process_dgram(data, addr)
            except Exception as e:
                # something wrong with packet rx, log and carry on
                print >>globals.ibus_log, "Error: " + e.message

    def destroy(self):
        """
        Closes socket
        """
        try:
            print >>globals.ibus_log, "Destroying UDP service..."
            self.sock.close()
        except (TypeError, Exception):
            pass

        self.sock = None
        self.thread = None
        
    def csum(self, data):
        checksum = 0
        for el in data:
            checksum ^= ord(el)
        return checksum

    def process_dgram(self, data, addr):
        checksum = self.csum(data)
            
        if globals.debug:
            print >>globals.ibus_log, addr, "udp_rx: " + data.encode("hex") + " cs: " + hex(checksum)
        
        globals.ibus_service.write_to_ibus(data + chr(checksum))
        
    def notify(self, msg):
        xbmcgui.Dialog().notification('BMW', msg, xbmcgui.NOTIFICATION_INFO, 2000)
        if globals.notify_ike:
            data = "681980234130".decode("hex") + msg[0:20].center(20)
            checksum = self.csum(data) 
            globals.ibus_service.write_to_ibus(data + chr(checksum))
 
    def send_packets_to_udp(self, ibus_packets):
        try:
            for ibus_packet in ibus_packets:
                if globals.debug:
                    print >>globals.ibus_log, ibus_packet
                if ibus_packet.source_id == "68": # Radio
                    if ibus_packet.destination_id == "f0" and ibus_packet.data[0:2] == "4a":
                        print >>globals.ibus_log, "Radio ping, responding"
                        resp = "f004684b05d2".decode("hex")
                        globals.ibus_service.write_to_ibus(resp)
                    elif ibus_packet.destination_id == "3b": # Nav/Video module
                        if ibus_packet.data[0:6] == "236210":
                            mode = ibus_packet.data[6:len(ibus_packet.data)].decode("hex").strip()
                            print >>globals.ibus_log, "Nav/Video Title message: " + mode
                            self.notify(mode)
                elif ibus_packet.source_id == "50" and ibus_packet.data[0:2] == "3b": # Steering buttons#
                    player = xbmc.Player()
                    if ibus_packet.data[2:4] == "21":
                        player.playnext()
                    elif ibus_packet.data[2:4] == "28":
                        player.playprevious() 
                    
                self.sock.sendto(ibus_packet.raw, (self.ip_addr, self.sendport))

            return True

        except Exception as e:
            # socket was closed, graceful restart
            print >>globals.ibus_log, "Error: " + e.message
            globals.restart_udp()
            return False

