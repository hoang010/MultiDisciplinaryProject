from RPi.PC import PC
from RPi.Tablet import Tablet
import threading


def main():

    # Initialise required stuff here
    ip_address = ''
    port = ''
    host_mac_addr = ''

    # Connect to PC
    pc = PC(ip_address, port)
    pc_connection = threading.Thread(target=pc.connect())

    # Connect to tablet
    tablet = Tablet(host_mac_addr)
    tablet_connection = threading.Thread(target=tablet.connect())

    print(bcolors.BOLD + 'PC connection running on thread 1.' + bcolors.ENDC)
    pc_connection.start()

    print(bcolors.BOLD + 'Tablet connection running on thread 2.' + bcolors.ENDC)
    tablet_connection.start()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
