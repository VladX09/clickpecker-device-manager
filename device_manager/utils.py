import configparser
import pathlib
import logging
import shlex
import subprocess
import logging
import json
import os

from logging import config

CONFIG_PATH = "configs/device_manager.conf"
LOGGING_CONFIG_PATH = "configs/logger.json"

logger = logging.getLogger("device_manager.utils")
proj_dir = pathlib.Path(os.path.dirname(__file__)).parent

def get_config_path():
    path =  proj_dir / CONFIG_PATH
    return path


def get_logging_config_path():
    path = proj_dir / LOGGING_CONFIG_PATH
    return path


def get_main_config():
    conf_path = get_config_path()
    config = configparser.ConfigParser()
    config.read(conf_path)
    return config


def get_whitelist_devices():
    config = get_main_config()
    return json.loads(config.get("Basic Config", "whitelist_devices"))


def get_blacklist_devices():
    config = get_main_config()
    return json.loads(config.get("Basic Config", "blacklist_devices"))


def configure_logger():
    def filename_parse_hook(data):
        if data.get("filename") is not None:
            filename = pathlib.Path(data["filename"])
            filename = proj_dir / filename
            filename.parent.mkdir(parents=True, exist_ok=True)
            data["filename"] = filename
        return data

    logging_path = get_logging_config_path()
    with open(logging_path) as f:
        conf = json.load(f, object_hook=filename_parse_hook)
        logging.config.dictConfig(conf)


def perform_cmd(cmd):
    logger = logging.getLogger("device_manager.utils.perform_cmd")
    process = subprocess.run(
        shlex.split(cmd), stdout=subprocess.PIPE, encoding="UTF-8")

    logger.debug("Performing cmd: {}".format(cmd))
    # logger.debug("Performing cmd: {}, result: {}".format(cmd, process))
    return process.stdout
