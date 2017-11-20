from flask import Flask, json
from device_manager import app
from unittest import mock
import pytest


def test_post_junk(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.post(
        "/acquire",
        data=json.dumps({
            "junk_field": "junk_value"
        }),
        content_type="application/json")

    assert response.status_code == 200
    device = json.loads(response.get_data())
    assert device["adb_id"] == "device_0"


def test_post_any(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.post(
        "/acquire", data=json.dumps({}), content_type="application/json")

    assert response.status_code == 200
    device = json.loads(response.get_data())
    assert device["adb_id"] == "device_0"


def test_post_valid_filter(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    response = client.post(
        "/acquire",
        data=json.dumps({
            "filters": {
                "android_version__ge": "4.4.4"
            }
        }),
        content_type="application/json")
    assert response.status_code == 200
    device = json.loads(response.get_data())
    expected_devices = {
        id
        for id, dev in test_devices.items() if dev.android_version >= "4.4.4"
    }
    assert device["adb_id"] in expected_devices


def test_acquire_release(mocked_get_mini_provider, test_devices):
    client = app.app.test_client()
    adb_id = "device_2"
    req = json.dumps({"filters": {"adb_id": adb_id}})
    response_acq = client.post("/acquire", data=req, content_type="application/json")
    assert response_acq.status_code == 200

    response_acq_fail = client.post("/acquire", data=req, content_type="application/json")
    assert response_acq_fail.status_code == 404
    assert json.loads(response_acq_fail.get_data())["error"] == "All such devices are busy"

    response_rel = client.post("/release", data=req, content_type="application/json")
    assert response_rel.status_code == 200

    response_rel = client.post("/release", data=req, content_type="application/json")
    assert response_rel.status_code == 200



