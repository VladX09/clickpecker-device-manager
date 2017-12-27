import re
import logging
import copy

from packaging import version
from device_manager import utils

logger = logging.getLogger("device_manager.device_record")


class Device:
    def __init__(self,
                 adb_id=None,
                 device_name=None,
                 status=None,
                 android_version=None,
                 sdk_version=None,
                 minicap_port=None,
                 minitouch_port=None,
                 stf_address=None,
                 free=True):
        self.adb_id = adb_id
        self.device_name = device_name
        self.status = status
        self.android_version = android_version
        self.sdk_version = sdk_version
        self.minicap_port = minicap_port
        self.minitouch_port = minitouch_port
        self.stf_address = stf_address
        self.free = True

    @property
    def android_version(self):
        return self._android_version

    @android_version.setter
    def android_version(self, value):
        self._android_version = None if value is None else version.parse(value)

    @classmethod
    def from_dict(cls, data):
        allowed = ("adb_id", "device_name", "status", "android_version",
                   "sdk_version", "minicap_port", "minitouch_port",
                   "stf_address")
        args = {k: v for k, v in data.items() if k in allowed}
        return cls(**args)

    def __repr__(self):
        return repr(self.__dict__)

    def perform_adb_cmd(self, cmd):
        return utils.perform_cmd("adb -s {} {}".format(self.adb_id, cmd))

    def get_property(self, prop):
        return self.perform_adb_cmd("shell getprop {}".format(prop)).strip()

    def get_screen_size(self):
        size_regex = "init=[\d]{3,}x[\d]{3,}"
        width_regex = "DisplayWidth=[\d]{3,}"
        height_regex = "DisplayHeight=[\d]{3,}"

        dumpsys = self.perform_adb_cmd("shell dumpsys window")
        size_match = re.search(size_regex, dumpsys)

        if not size_match:
            width = re.search(width_regex, dumpsys)
            height = re.search(height_regex, dumpsys)

            if not width or not height:
                raise ValueError("Dumpsys does not contain display size")

            width = width.group(0).strip().replace("DisplayWidth=", "")
            height = height.group(0).strip().replace("DisplayHeight=", "")
            return "{}x{}".format(width, height)

        return size_match.group(0).strip().replace("init=", "")

    def check_app_running(self, name):
        lines = self.perform_adb_cmd(
            "shell 'ps |grep {}'".format(name)).split('\n')
        return (len(lines) > 0 and lines[0] != "")

    def kill_app(self, name):
        lines = self.perform_adb_cmd(
            "shell 'ps |grep {}'".format(name)).split('\n')
        pid = lines[0].split()[1]
        self.perform_adb_cmd("shell 'kill {}'".format(pid))

    def copy(self):
        return copy.copy(self)
