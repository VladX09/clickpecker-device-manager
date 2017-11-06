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
    devices = provider.get_devices(filters)
    return responses.ResponseSuccess(devices)
