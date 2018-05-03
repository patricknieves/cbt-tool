from stem import Signal
from stem.control import Controller


def change_ip():
    """ Changes the programs IP address """
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

