#!/usr/bin/env python
import globals
import signal
import sys
import time

import xbmc

def main():
    """
    Start core services
    """
    xbmc.log( "BMW IBUS/UDP Controller Starting services...", level=xbmc.LOGNOTICE )
    globals.start_services()

    monitor = xbmc.Monitor()
    
    # run until abort requested
    while not monitor.abortRequested():
        time.sleep(1)


if __name__ == "__main__":
    main()