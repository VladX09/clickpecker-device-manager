from device_manager.providers.device_provider import get_provider
from device_manager.providers.mini_provider import MiniDeviceProvider
from unittest import mock
import pytest


def test_without_filters(test_devices, mocked_mini_provider):
    devices = mocked_mini_provider.get_devices()
    assert devices == test_devices
    devices = mocked_mini_provider.get_devices({})
    assert devices == test_devices


def test_filters_eq(mocked_mini_provider):
    devices = mocked_mini_provider.get_devices({"adb_id": "device_1"})
    print(devices)
    assert len(devices) == 1
    assert devices[0].adb_id == "device_1"

    devices = mocked_mini_provider.get_devices({"adb_id__eq": "device_1"})
    assert len(devices) == 1
    assert devices[0].adb_id == "device_1"


def test_filters_operations(test_devices, mocked_mini_provider):
    devices = mocked_mini_provider.get_devices({"sdk_version__lt": 19})
    assert len(devices) == len(
        [device for device in test_devices if device.sdk_version < 19])

    devices = mocked_mini_provider.get_devices({"sdk_version__le": 19})
    assert len(devices) == len(
        [device for device in test_devices if device.sdk_version <= 19])

    devices = mocked_mini_provider.get_devices({"sdk_version__gt": 19})
    assert len(devices) == len(
        [device for device in test_devices if device.sdk_version > 19])

    devices = mocked_mini_provider.get_devices({"sdk_version__ge": 19})
    assert len(devices) == len(
        [device for device in test_devices if device.sdk_version >= 19])

    devices = mocked_mini_provider.get_devices({"sdk_version__ne": 19})
    assert len(devices) == len(
        [device for device in test_devices if device.sdk_version != 19])


def test_filters_android_ver_intervals(test_devices, mocked_mini_provider):
    filters = {"android_version__ge": "4.2", "android_version__le": "5.0"}
    devices = mocked_mini_provider.get_devices(filters)
    filtered_ids = [device.adb_id for device in devices]
    not_filtered_devices = [
        device for device in test_devices if device.adb_id not in filtered_ids
    ]
    for filtered in devices:
        android_version = filtered.android_version
        assert ("4.2" in android_version or "4.3" in android_version
                or "4.4" in android_version or "5.0" in android_version)
    for remain in not_filtered_devices:
        android_version = remain.android_version
        assert not ("4.2" in android_version or "4.3" in android_version
                    or "4.4" in android_version or "5.0" in android_version)


def test_filters_sdk_ver_intarvals(test_devices, mocked_mini_provider):
    filters = {"sdk_version__gt": 17, "sdk_version__lt": 22}
    devices = mocked_mini_provider.get_devices(filters)
    filtered_ids = [device.adb_id for device in devices]
    not_filtered_devices = [
        device for device in test_devices if device.adb_id not in filtered_ids
    ]
    for filtered in devices:
        sdk_version = filtered.sdk_version
        assert sdk_version > 17 and sdk_version < 22
    for remain in not_filtered_devices:
        sdk_version = remain.sdk_version
        assert sdk_version <= 17 or sdk_version >= 22


def test_filters_device_id(mocked_mini_provider):
    id = "device_5"
    filters = {"adb_id": id}
    devices = mocked_mini_provider.get_devices(filters)
    assert len(devices) == 1
    assert devices[0].adb_id == id


def test_filters_device_name(mocked_mini_provider):
    name = "Test Device 5"
    filters = {"device_name__eq": name}
    devices = mocked_mini_provider.get_devices(filters)
    assert len(devices) == 1
    assert devices[0].device_name == name


wrong_value_type_filters = [{
    "device_name": 123456
}, {
    "android_version__le": 4.4
}, {
    "sdk_version__gt": "19"
}, {
    "status": ["online", "offline"]
}, {
    "android_version__ne": 4.4
}]


@pytest.mark.parametrize("_filter", wrong_value_type_filters)
def test_filters_wrong_value_types(mocked_mini_provider, _filter):
    with pytest.raises(TypeError):
        devices = mocked_mini_provider.get_devices(_filter)


wrong_operator_filters = [{
    "device_name__in": "AbcDef"
}, {
    "sdk_version__bull_shit": 19
}]


@pytest.mark.parametrize("_filter", wrong_operator_filters)
def test_filters_wrong_operators(mocked_mini_provider, _filter):
    with pytest.raises(NotImplementedError):
        devices = mocked_mini_provider.get_devices(_filter)
