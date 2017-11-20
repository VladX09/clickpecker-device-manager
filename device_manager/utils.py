import configparser
import pathlib
import logging
import shlex
import subprocess
import logging
import json
import os.path

from logging import config

CONFIG_PATH = "configs/device_manager.conf"
LOGGING_CONFIG_PATH = "configs/logger.json"

logger = logging.getLogger("device_manager.utils")


def get_config_path():
    return pathlib.Path(os.path.dirname(__file__)) / CONFIG_PATH


def get_logging_config_path():
    return pathlib.Path(os.path.dirname(__file__)) / LOGGING_CONFIG_PATH


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
    logging_path = get_logging_config_path()
    with open(logging_path) as f:
        conf = json.load(f)
        logging.config.dictConfig(conf)


def perform_cmd(cmd):
    logger = logging.getLogger("device_manager.utils.perform_cmd")
    process = subprocess.run(
        shlex.split(cmd), stdout=subprocess.PIPE, encoding="UTF-8")
    logger.debug("Performing cmd: {}, result: {}".format(cmd, process))
    return process.stdout
