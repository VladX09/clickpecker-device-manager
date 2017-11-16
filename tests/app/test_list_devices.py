from flask import Flask, json
from device_manager import app
from unittest import mock
import pytest


def test_get(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    devices = json.loads(response.get_data())
    assert len(devices) == len(test_devices)


def test_post_empty(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.post("/")

    assert response.status_code == 400
    assert "Invalid POST" in json.loads(response.get_data())["error"]


def test_post_json_none(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.post("/", data=json.dumps(None), content_type="application/json")

    assert response.status_code == 400
    assert "Invalid POST" in json.loads(response.get_data())["error"]


def test_post_junk(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.post(
        "/",
        data=json.dumps({
            "junk_field": "junk_value"
        }),
        content_type="application/json")

    assert response.status_code == 200
    devices = json.loads(response.get_data())
    assert len(devices) == len(test_devices)


def test_post_any(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.post(
        "/",
        data=json.dumps({}),
        content_type="application/json")

    assert response.status_code == 200
    devices = json.loads(response.get_data())
    assert len(devices) == len(test_devices)


def test_post_valid_filter(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.post(
        "/",
        data=json.dumps({
            "filters": {
                "android_version__ge": "4.4.4"
            }
        }),
        content_type="application/json")
    assert response.status_code == 200
    devices = json.loads(response.get_data())
    expected_devices = {
        id
        for id, dev in test_devices.items() if dev.android_version >= "4.4.4"
    }
    devices = {dev["adb_id"] for dev in devices}
    assert devices == expected_devices


@pytest.mark.parametrize("filters, status_code, msg", [
    ({"sdk_version__in": [11, 12]}, 500, "NotImplementedError"),
    ({"junk_param":12}, 500,"AttributeError"),
    ({"adb_id":11}, 500, "TypeError"),
    ({"sdk_version__gt":""}, 500, "TypeError"),
    ({"adb_id":None}, 500, "TypeError"),
    ({None:None}, 500, "AttributeError"),
    (None, 400, "filters: is not a")
])
def test_post_invalid_filter(
        mocked_get_mini_provider,
        test_devices,
        filters,
        status_code,
        msg
):
    client = app.app.test_client()
    response = client.post(
        "/", data=json.dumps({"filters": filters}), content_type="application/json")

    assert response.status_code == status_code
    assert msg in json.loads(response.get_data())["error"]
