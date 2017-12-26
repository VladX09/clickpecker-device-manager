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
    responses.ResponseFailure.RESOURCE_ERROR: 404,
    responses.ResponseFailure.PARAMETERS_ERROR: 400,
    responses.ResponseFailure.SYSTEM_ERROR: 500
}


@app.route("/", methods=["GET", "POST"])
def list_devices():
    return _handle_obtain_request(request, obtain_cases.list_devices)


@app.route("/acquire", methods=["POST"])
def acquire_device():
    return _handle_obtain_request(request, obtain_cases.acquire_device)


@app.route("/release", methods=["POST"])
def release_device():
    return _handle_obtain_request(request, obtain_cases.release_device)


def _handle_obtain_request(request, use_case):
    provider = get_provider()

    if request.method == "POST":
        body = request.get_json()
        if body is None:
            return Response(
                json.dumps({"error":"Invalid POST body. Please, check your request body and content type."}),
                status=400)
        logger.info("Receiving POST request with body: {}".format(body))
        case_request = requests.DeviceObtainRequest.from_dict(body)
    else:
        logger.info("Receiving GET request".format(body))
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
