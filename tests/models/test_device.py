from device_manager.models.device import Device
from unittest import mock
import pytest

device_spec = {
    "adb_id": "test_id",
    "device_name": "Test Device",
    "status": "device",
    "android_version": "4.4.1",
    "sdk_version": 19,
    "minicap_port": 1111,
    "minitouch_port": 1112,
    "stf_address": "localhost:1111",
    "redundant_field": "some_trash"
}


def test_from_dict():
    device = Device.from_dict(device_spec)
    assert device.adb_id == device_spec["adb_id"]
    assert device.device_name == device_spec["device_name"]
    assert device.status == device_spec["status"]
    assert device.android_version == device_spec["android_version"]
    assert device.sdk_version == device_spec["sdk_version"]
    assert device.minicap_port == device_spec["minicap_port"]
    assert device.minitouch_port == device_spec["minitouch_port"]
    assert device.stf_address == device_spec["stf_address"]
    with pytest.raises(AttributeError):
        device.redundant_field


@mock.patch("device_manager.utils.perform_cmd")
def test_perform_adb_cmd(mock_perform_cmd):
    device = Device.from_dict(device_spec)
    device.perform_adb_cmd("test cmd")
    mock_perform_cmd.assert_called_with("adb -s test_id test cmd")


dumps_positive = [
    "Somestring init=1280x120 somestring \n somestring",
    "Somestringinit=1280x120somestring \n somestring",
    "Somestring DisplayWidth=1280x120 \n DisplayHeight=120, somestring \n somestring",
    "Somestring with double init=1280x120 init=1380x130",
    "SomestringDisplayWidth=1280x120DisplayHeight=120,somestring \n somestring"
]


@pytest.mark.parametrize("dumpsys", dumps_positive)
@mock.patch("device_manager.utils.perform_cmd")
def test_get_screen_size_positive(mock_perform_cmd, dumpsys):
    mock_perform_cmd.return_value = dumpsys
    device = Device(device_spec)
    assert device.get_screen_size() == "1280x120"


dumps_negative = [
    "Somestring without init= or DisplayHeight= or DisplayWidth=",
    "Somestring with wrong init=1 or init=x10",
    "Somestring with DisplayWidth=123 but without DisplayHeight"
]

@pytest.mark.parametrize("dumpsys", dumps_negative)
@mock.patch("device_manager.utils.perform_cmd")
def test_get_screen_size_negative(mock_perform_cmd, dumpsys):
    mock_perform_cmd.return_value = dumpsys
    device = Device(device_spec)
    with pytest.raises(ValueError):
        print(device.get_screen_size())

