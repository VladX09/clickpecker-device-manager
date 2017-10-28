import re

from configuration import perform_cmd


class DeviceRecord:
    adb_id = None
    device_name = None
    status = None
    android_version = None
    sdk_version = None
    minicap_port = None
    minitouch_port = None
    stf_address = None

    def perform_adb_cmd(self, cmd):
        return perform_cmd("adb -s {} {}".format(self.adb_id, cmd))

    def get_property(self, prop):
        return self.perform_adb_cmd("shell getprop {}".format(prop)).strip()

    def get_screen_size(self):
        size_regex = "init=[\d]*x[\d]*"
        dumpsys = self.perform_adb_cmd("shell dumpsys window")
        size_match = re.search(size_regex, dumpsys)
        if not size_match:
            width_regex = "DisplayWidth=[\d]*"
            height_regex = "DisplayHeight=[\d]*"
            width = re.search(width_regex, dumpsys).group(0).strip().replace(
                "DisplayWidth=", "")
            height = re.search(height_regex, dumpsys).group(0).strip().replace(
                "DisplayHeight=", "")
            return "{}x{}".format(width, height)
        return size_match.group(0).strip().replace("init=", "")

    def to_json():
        pass


def init_mini(adb_id, status):
    dev = DeviceRecord()
    dev.adb_id = adb_id
    dev.status = status
    return dev
