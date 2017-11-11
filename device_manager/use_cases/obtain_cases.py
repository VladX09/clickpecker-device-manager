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
def obtain_device(request, provider):
    filters = request.filters
    filters["free"] = True
    devices = provider.get_devices(filters)
    if len(devices) > 0:
        device = devices[0]
        provider.acquire_device(device)
        return responses.ResponseSuccess(device)
    else:
        return responses.ResponseFailure.resource_error(
            "No such device or device is busy")
