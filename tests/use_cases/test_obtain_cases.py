from device_manager.use_cases.obtain_cases import acquire_device, release_device
from device_manager.use_cases.requests import DeviceObtainRequest
from device_manager.use_cases.responses import ResponseSuccess, ResponseFailure
from device_manager.models.device import Device


def test_success(mocked_mini_provider):
    request = DeviceObtainRequest.from_dict({
        "filters": {
            "adb_id": "device_1"
        }
    })
    response = acquire_device(request, mocked_mini_provider)
    assert response.successfull()
    assert response.type == ResponseSuccess.SUCCESS
    assert isinstance(response.value, Device)
    assert response.value.adb_id == "device_1"


def test_fail_invalid_request(mocked_mini_provider):
    request = DeviceObtainRequest.from_dict({"something": 1, "something": "2"})
    response = acquire_device(request, mocked_mini_provider)
    assert not response.successfull()
    assert response.type == ResponseFailure.PARAMETERS_ERROR
    assert "filters: field is absent" in response.message


def test_fail_system_error(mocked_mini_provider):
    request = DeviceObtainRequest.from_dict({"filters": {"adb_id__smt": "a"}})
    response = acquire_device(request, mocked_mini_provider)
    assert not response.successfull()
    assert response.type == ResponseFailure.SYSTEM_ERROR
    assert "NotImplementedError" in response.message

    request = DeviceObtainRequest.from_dict({"filters": {"adb_id": 123}})
    response = acquire_device(request, mocked_mini_provider)
    assert not response.successfull()
    assert response.type == ResponseFailure.SYSTEM_ERROR
    assert "TypeError" in response.message


def test_fail_resource_error(mocked_mini_provider):

    # Acquire device - device is free
    request = DeviceObtainRequest.from_dict({
        "filters": {
            "adb_id": "device_1"
        }
    })
    response = acquire_device(request, mocked_mini_provider)
    assert response.successfull()
    assert response.type == ResponseSuccess.SUCCESS
    assert isinstance(response.value, Device)
    assert response.value.adb_id == "device_1"

    # Acquire again - device is busy
    response = acquire_device(request, mocked_mini_provider)
    assert not response.successfull()
    assert response.type == ResponseFailure.RESOURCE_ERROR
    assert "No such device" in response.message


def test_acquire_and_release(mocked_mini_provider):

    # Acquire device
    request_acquire = DeviceObtainRequest.from_dict({
        "filters": {
            "android_version": "5.0"
        }
    })
    response = acquire_device(request_acquire, mocked_mini_provider)
    assert response.successfull()
    assert isinstance(response.value, Device)
    assert response.value.adb_id == "device_6"

    # Release device
    request_release = DeviceObtainRequest.from_dict({
        "filters": {
            "adb_id": response.value.adb_id
        }
    })
    response = release_device(request_release, mocked_mini_provider)
    assert response.successfull()
    assert isinstance(response.value, Device)
    assert response.value.adb_id == "device_6"

    # Acquire again - device is free
    response = acquire_device(request_acquire, mocked_mini_provider)
    assert response.successfull()
    assert isinstance(response.value, Device)
    assert response.value.adb_id == "device_6"

    # Acquire again - device is busy
    response = acquire_device(request_acquire, mocked_mini_provider)
    assert not response.successfull()
    assert "busy" in response.message