import pytest
from device_manager.models.device import Device
from device_manager.providers.mini_provider import MiniDeviceProvider
from unittest import mock


@pytest.fixture
def test_devices():
    devices = {}
    statuses = ["offline", "device"]
    android_and_sdk = {
        "4.1.1": 16,
        "4.2": 17,
        "4.2.0": 17,
        "4.4": 19,
        "4.4.4": 19,
        "4.4.2": 19,
        "5.0": 21,
        "5.1": 22,
        "8.0.0": 26,
        "8.0": 26
    }
    for i, (android_version,
            sdk_version) in enumerate(android_and_sdk.items()):
        adb_id = "device_{}".format(i)
        device_name = "Test Device {}".format(i)
        status = statuses[i % 2]
        minicap_port = 1110 + i
        minitouch_port = 1110 + i
        stf_address = "//stf/device/{}".format(i)
        device = Device(adb_id, device_name, status, android_version,
                        sdk_version, minicap_port, minitouch_port, stf_address)
        devices[adb_id] = device
    return devices


@pytest.fixture
def mocked_mini_provider(test_devices):
    with mock.patch.object(
            MiniDeviceProvider, "_get_devices_from_adb",
            autospec=True) as mock_get_devices_from_adb:
        mock_get_devices_from_adb.return_value = test_devices
        provider = MiniDeviceProvider(1110, 1110 + 2 * len(test_devices),
                                      "./minicap_root", "./minitouch_root")
        # device_ids = [device.adb_id for device in test_devices]
        # provider.devices = dict(zip(device_ids, test_devices))
        yield provider
