import time
from ibus_service.ibus import IBUSService
from udp_service.udp import UDPService

# global services
udp_service = None
debug = True
notify_ike = True
ibus_service = None
ibus_log = None


def start_services(auto_retry=True):
    """
    Main method of the Rasperry Pi service(s)
    """
    # initialize ibus and udp services
    global ibus_service, udp_service, ibus_log
    try:
        ibus_log = open('/storage/ibuspy.log', 'a')
        print "Initializing IBUS service...."
        ibus_service = IBUSService()
        print "Initializing UDP service...."
        udp_service = UDPService()
        print "All services running..."
    except Exception as e:
        if auto_retry:
            print "Error: " + e.message + "\n" + "Failed to kodiservice, trying again in 5 seconds..."
            time.sleep(5)
            print "Restarting now...\n"
            start_services()
        return


def restart_services():
    """
    Destroys existing IBUS and UDP communication and re-initializes
    """
    print "Restarting services..."
    stop_services()
    start_services()


def restart_udp():
    """
    Restarts UDP communication and enters listening mode
    """
    print "Restarting UDP service..."
    global udp_service
    if udp_service is not None:
        udp_service.destroy()
    udp_service = UDPService()


def stop_services():
    """
    Destroys IBUS and UDP services
    """
    if ibus_service is not None:
        ibus_service.destroy()
    if udp_service is not None:
        udp_service.destroy()