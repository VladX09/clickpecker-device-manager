from device_manager.providers.ports_pool import PortsPool
from unittest import mock
import pytest


@pytest.mark.parametrize(("start_port", "end_port"),
                         [(1111, '1110'), ('1111', '1111'), ('string', 1112),
                          ([1, 2, 3], [])])
def test_init_wrong_value_type(start_port, end_port):
    with pytest.raises(TypeError):
        pool = PortsPool(start_port, end_port)
        port = pool.get_port()
        port2 = pool.get_port()
        print(port, " : ", port2)


@pytest.mark.parametrize(("start_port", "end_port"), [
    (1111, 1110),
    (1111, 1111),
    (1111, 1112),
])
def test_init_wrong_values(start_port, end_port):
    with pytest.raises(ValueError):
        pool = PortsPool(start_port, end_port)


def test_positive():
    start_port = 1111
    device_num = 5
    end_port = start_port + 2 * device_num

    for k in range(0, 2):
        pool = PortsPool(start_port, end_port)
        used_ports = []
        for i in range(0, 2 * device_num):
            used_ports.append(pool.get_port())
        assert len(used_ports) == end_port - start_port
        assert len(used_ports) == len(set(used_ports))

        for port in used_ports:
            pool.release_port(port)


def test_key_error():
    start_port = 1111
    device_num = 3
    end_port = start_port + 2 * device_num

    for k in range(0, 2):
        pool = PortsPool(start_port, end_port)
        used_ports = []
        with pytest.raises(KeyError):
            for i in range(0, 2 * device_num + 1):
                used_ports.append(pool.get_port())
