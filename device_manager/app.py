from flask import Flask, request, Response, json

import logging

from device_manager.use_cases import obtain_cases
from device_manager.use_cases import requests
from device_manager.use_cases import responses
from device_manager.models import device
from device_manager.providers import get_provider
from device_manager.serializers.device_encoder import DeviceEncoder
from device_manager import utils

app = Flask(__name__)
utils.configure_logger()
logger = logging.getLogger("device_manager")

STATUS_CODES = {
    responses.ResponseSuccess.SUCCESS: 200,
    responses.ResponseFailure.RESOURCE_ERROR_NOT_FOUND: 404,
    responses.ResponseFailure.RESOURCE_ERROR_BUSY: 409,
    responses.ResponseFailure.PARAMETERS_ERROR: 400,
    responses.ResponseFailure.SYSTEM_ERROR: 500
}


@app.route("/", methods=["GET", "POST"])
def list_devices():
    """Return list of available devices.

    **Example response**:

    .. sourcecode:: http

        HTTP/1.0 200 OK
        Content-Length: 200
        Content-Type: application/json

        [
            {
                "adb_id": "BL4B22D10786",
                "android_version": "4.4.4",
                "device_name": "D2203",
                "free": true,
                "minicap_port": 1111,
                "minitouch_port": 1112,
                "sdk_version": 19,
                "status": "device",
                "stf_address": null
            }
        ]

    """

    return _handle_obtain_request(request, obtain_cases.list_devices)


@app.route("/acquire", methods=["POST"])
def acquire_device():
    """Find device by the given filter and make it unavailable for other clients to acquire.

    :<json dict filters: filters to find necessary device, see :ref:`filters-specification`
    :status 200: Device successfully acquired
    :status 400: Invalid request body
    :status 404: No suitable device found
    :status 409: All suitable devices are locked by another clients
    :status 500: Internal server error
    :returns: JSON with device specifications (as in :meth:`list_devices`) or error description

    **Unsuccessfull response example**:

    .. sourcecode:: http

        HTTP/1.0 404 NOT FOUND
        Content-Length: 28
        Content-Type: application/json

        {
            "error": "No such devices"
        }

    """

    return _handle_obtain_request(request, obtain_cases.acquire_device)


@app.route("/release", methods=["POST"])
def release_device():
    """Release acquired device.

    **It's highly recommended to store ADB ID of acquiring device and use it for releasing**.

    :<json dict filters: filters to find the necessary device, see :ref:`filters-specification`
    :status 200: Device successfully released (or not found / unplugged from host machine)
    :status 400: Invalid request body
    :status 500: Internal server error

    """

    return _handle_obtain_request(request, obtain_cases.release_device)


def _handle_obtain_request(request, use_case):
    provider = get_provider()

    if request.method == "POST":
        body = request.get_json()
        # TODO: add correct mimetype
        if body is None:
            return Response(
                json.dumps({
                    "error":
                    "Invalid POST body. Please, check your request body and content type."
                }),
                status=400)
        logger.info("Receiving POST request with body: {}".format(body))
        case_request = requests.DeviceObtainRequest.from_dict(body)
    else:
        logger.info("Receiving GET request")
        case_request = requests.DeviceObtainRequest.from_dict({})

    case_response = use_case(case_request, provider)
    return _prepare_obtain_response(case_response)


def _prepare_obtain_response(case_response):
    if case_response.successfull():
        body = json.dumps(case_response.value, cls=DeviceEncoder)
    else:
        body = json.dumps({"error": case_response.message})
    logger.info("Sending response with body: {}".format(body))
    return Response(
        body,
        mimetype="application/json",
        status=STATUS_CODES[case_response.type])
