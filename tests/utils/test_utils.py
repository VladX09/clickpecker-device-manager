import json
from device_manager import utils


def test_config_path():
    path = utils.get_config_path()
    assert path.exists()


def test_logging_config_path():
    path = utils.get_logging_config_path()
    assert path.exists()


def test_main_config():
    config = utils.get_main_config()
    items = [
        "type", "start_port", "max_devices", "minicap_root", "minitouch_root",
        "whitelist_devices", "blacklist_devices"
    ]
    for item in items:
      assert item in config["Basic Config"]


def test_whitelist():
    whitelist = utils.get_whitelist_devices()
    assert isinstance(whitelist, list)


def test_blacklist():
    blacklist = utils.get_blacklist_devices()
    assert isinstance(blacklist, list)
