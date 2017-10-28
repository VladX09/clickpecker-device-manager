import subprocess
import configparser
import pathlib
import shlex

CONFIG_PATH = "device_manager.conf"


# TODO: find the right place for it
def perform_cmd(cmd):
    process = subprocess.run(
        shlex.split(cmd), stdout=subprocess.PIPE, encoding="UTF-8")
    return process.stdout


class PortsPool:
    def __init__(self, start_port, end_port):
        #TODO: add ports validation here
        if not (end_port - start_port % 2):
            raise RuntimeError(
                "The pool should contain an even number of ports")
        self.free_ports = set(range(start_port, end_port))
        self.busy_ports = set()

    def get_port(self):
        # TODO: add KeyError catch into caller
        port = self.free_ports.pop()
        self.busy_ports.add(port)
        return port

    def release_port(self, port):
        #TODO: add port validation here
        self.busy_ports.discard(port)
        self.free_ports.add(port)


def get_main_config():
    conf_path = pathlib.Path(CONFIG_PATH)
    config = configparser.ConfigParser()
    config.read(conf_path)
    return config
