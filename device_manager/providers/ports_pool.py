class PortsPool:
    def __init__(self, start_port, end_port):
        if (end_port - start_port) % 2 != 0 or end_port <= start_port:
            raise ValueError("The pool should contain an even number of ports")
        self.free_ports = set(range(start_port, end_port))
        self.busy_ports = set()

    def get_port(self):
        # Raises KeyError if no free ports
        port = self.free_ports.pop()
        self.busy_ports.add(port)
        return port

    def release_port(self, port):
        self.busy_ports.discard(port)
        self.free_ports.add(port)
