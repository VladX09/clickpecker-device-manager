import configparser
import pathlib
import logging
import shlex
import subprocess
import logging


CONFIG_PATH = "device_manager.conf"
LOGGING_CONFIG_PATH = "logger.json"

logger = logging.getLogger("device_manager.utils")


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

def configure_logger():
    with open(LOGGING_CONFIG_PATH) as f:
        conf = json.load(f)
        logging.config.dictConfig(conf)

def perform_cmd(cmd):
    logger = logging.getLogger("device_manager.utils.perform_cmd")
    process = subprocess.run(
        shlex.split(cmd), stdout=subprocess.PIPE, encoding="UTF-8")
    logger.debug("Performing cmd: {}, result: {}".format(cmd, process))
    return process.stdout

