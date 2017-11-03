import configparser
import pathlib
import logging

CONFIG_PATH = "device_manager.conf"

logger = logging.getLogger("device_manager.configuration")


class PortsPool:
    def __init__(self, start_port, end_port):
        if not (end_port - start_port % 2):
            raise RuntimeError(
                "The pool should contain an even number of ports")
        self.free_ports = set(range(start_port, end_port))
        self.busy_ports = set()

    def get_port(self):
        # Raise KeyError if no free ports
        port = self.free_ports.pop()
        self.busy_ports.add(port)
        return port

    def release_port(self, port):
        self.busy_ports.discard(port)
        self.free_ports.add(port)


def get_main_config():
    conf_path = pathlib.Path(CONFIG_PATH)
    config = configparser.ConfigParser()
    config.read(conf_path)
    return config
