from device_manager.use_cases import responses


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
def get_device_list(request, provider):
    filters = request.filters
    devices = provider.get_devices(filters)
    return responses.ResponseSuccess(devices)


@basic_use_case_validation
def acquire_device(request, provider):
    request.filters["free"] = True
    response = get_device_list(request, provider)
    if not response.successfull():
        return response

    devices = response.value
    if len(devices) > 0:
        device = devices[0]
        provider.acquire_device(device)
        return responses.ResponseSuccess(device)
    else:
        return responses.ResponseFailure.resource_error(
            "No such devices or devices are busy")


@basic_use_case_validation
def release_device(request, provider):
    request.filters["free"] = False
    response = get_device_list(request, provider)
    if not response.successfull():
        return response

    device = response.value[0]
    provider.release_device(device)
    return responses.ResponseSuccess(device)
