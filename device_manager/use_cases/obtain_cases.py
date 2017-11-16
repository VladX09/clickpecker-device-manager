from device_manager.use_cases import responses
import logging

logger = logging.getLogger("device_manager.use_cases")

def basic_use_case_validation(use_case):
    def wrapped(request, *args, **kwargs):
        if not request.valid():
            return responses.ResponseFailure.invalid_request(request)
        try:
            return use_case(request, *args, **kwargs)
        except Exception as e:
            return responses.ResponseFailure.system_error(e)

    return wrapped


@basic_use_case_validation
def list_devices(request, provider):
    filters = request.filters
    devices = provider.get_devices(filters)
    return responses.ResponseSuccess(devices)


@basic_use_case_validation
def acquire_device(request, provider):
    response = list_devices(request, provider)

    if not response.successfull():
        return response

    devices = response.value
    if len(devices) == 0:
        return responses.ResponseFailure.resource_error("No such devices")

    free_devices = [dev for dev in devices if dev.free]
    if len(free_devices) == 0:
        return responses.ResponseFailure.resource_error(
            "All such devices are busy")

    device = free_devices[0]
    provider.acquire_device(device)
    logger.info("Device '{}' acquired".format(device.adb_id))
    return responses.ResponseSuccess(device)


@basic_use_case_validation
def release_device(request, provider):
    request.filters["free"] = False
    response = list_devices(request, provider)
    if not response.successfull():
        return response

    devices = response.value
    if len(devices) > 1:
        return responses.ResponseFailure.parameters_error(
            "Filter is ambiguous: {} devices were found".format(
                len(devices)))

    if len(devices) == 1:
        device = devices[0]
        provider.release_device(device)

    return responses.ResponseSuccess("Device was released")
