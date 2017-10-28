import subprocess


# TODO: find the right place for it
def perform_cmd(cmd):
    process = subprocess.run(
        cmd.split(), stdout=subprocess.PIPE, encoding="UTF-8")
    return process.stdout


class PortsPool:
    def __init__(self, min_port, max_port):
        #TODO: add ports validation here
        if not (max_port - min_port % 2):
            raise RuntimeError(
                "The pool should contain an even number of ports")
        self.free_ports = set(range(min_port, max_port))
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
