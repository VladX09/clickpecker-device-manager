import device_manager.use_cases.responses


def basic_use_case_validation(use_case, request, *args, **kwargs):
    if not request.valid():
        return responses.ResponseFailure.invalid_request(request)
    try:
        return use_case(request, *args, **kwargs)
    except Exception as e:
        return responses.ResponseFailure.system_error(e)


@basic_use_case_validation
def obtain_device(request, provider):
    filters = request.filters
    filters["free"] = True
    devices = provider.get_devices(filters)
    if len(devices) > 0:
        device = devices[0]
        provider.acquire(device)
        return responses.ResponseSuccess(device)
    else:
        return responses.ResponseFailure.resource_arror(
            "No such device or device is busy")
