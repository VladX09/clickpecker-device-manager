from device_manager.use_cases.obtain_cases import obtain_device
from device_manager.use_cases.requests import DeviceObtainRequest
from device_manager.use_cases.responses import ResponseSuccess, ResponseFailure
from device_manager.models.device import Device


def test_success(mocked_mini_provider):
    request = DeviceObtainRequest.from_dict({
        "filters": {
            "adb_id": "device_1"
        }
    })
    response = obtain_device(request, mocked_mini_provider)
    assert response.successfull()
    assert response.type == ResponseSuccess.SUCCESS
    assert isinstance(response.value, Device)
    assert response.value.adb_id == "device_1"


def test_fail_invalid_request(mocked_mini_provider):
    request = DeviceObtainRequest.from_dict({"something": 1, "something": "2"})
    response = obtain_device(request, mocked_mini_provider)
    assert not response.successfull()
    assert response.type == ResponseFailure.PARAMETERS_ERROR
    assert "filters: field is absent" in response.message


def test_fail_system_error(mocked_mini_provider):
    request = DeviceObtainRequest.from_dict({"filters": {"adb_id__smt": "a"}})
    response = obtain_device(request, mocked_mini_provider)
    assert not response.successfull()
    assert response.type == ResponseFailure.SYSTEM_ERROR
    assert "NotImplementedError" in response.message

    request = DeviceObtainRequest.from_dict({"filters": {"adb_id": 123}})
    response = obtain_device(request, mocked_mini_provider)
    assert not response.successfull()
    assert response.type == ResponseFailure.SYSTEM_ERROR
    assert "TypeError" in response.message


def test_fail_resource_error(mocked_mini_provider):
    request = DeviceObtainRequest.from_dict({
        "filters": {
            "adb_id": "device_1"
        }
    })
    response = obtain_device(request, mocked_mini_provider)
    assert response.successfull()
    assert response.type == ResponseSuccess.SUCCESS
    assert isinstance(response.value, Device)
    assert response.value.adb_id == "device_1"
    response = obtain_device(request, mocked_mini_provider)
    assert not response.successfull()
    assert response.type == ResponseFailure.RESOURCE_ERROR
    assert "No such device" in response.message
