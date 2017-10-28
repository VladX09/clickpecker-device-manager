import json
import subprocess
import re
import os
import shlex
import logging
import configuration
import device_record
from configuration import perform_cmd

from pathlib import Path, PurePosixPath

PROP_ANDROID_VERSION = "ro.build.version.release"
PROP_DEVICE_NAME = "ro.product.model"
PROP_SDK_VERSION = "ro.build.version.sdk"
PROP_ABI = "ro.product.cpu.abi"
PROP_PREVIEW = "ro.build.version.preview_sdk"


class DeviceProvider:
    """Provider interface
    TODO: use zope.interface to make it strict?
    """

    def get_device_by_spec(self, json_spec):
        pass

    def get_device_list(self):
        pass


class MiniDeviceProvider(DeviceProvider):
    def __init__(self, min_port, max_port):
        self.ports_pool = configuration.PortsPool(min_port, max_port)

    def launch_minitouch(self, device, minitouch_root):
        abi = device.get_property(PROP_ABI)
        if device.sdk_version >= 16:
            bin = "minitouch"
        else:
            bin = "minitouch-nopie"
        minitouch_path = minitouch_root / "libs" / abi / bin
        device_dir = PurePosixPath("/data/local/tmp")
        device.perform_adb_cmd("push {} {}".format(minitouch_path, device_dir))

        start_cmd = "adb -s {id} shell {path}".format(
            id=device.adb_id, path=device_dir / bin)
        subprocess.Popen(
            shlex.split(start_cmd),
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL)

        port = self.ports_pool.get_port()
        device.perform_adb_cmd(
            "forward tcp:{} localabstract:minitouch".format(port))
        print("Start CMD: ", start_cmd)
        print("Minitouch: ", minitouch_path)
        print("Port: ", port)
        return port

    def launch_minicap(self, device, minicap_root):
        # minicap_root is pathlib Path !
        port = self.ports_pool.get_port()
        abi = device.get_property(PROP_ABI)
        pre = device.get_property(PROP_PREVIEW)
        if pre:
            sdk = device.sdk_version + 1
        else:
            sdk = device.sdk_version
        rel = device.android_version

        if sdk >= 16:
            bin = "minicap"
        else:
            bin = "minicap-nopie"

        size = device.get_screen_size()
        args = "-P {}@{}/0".format(size, size)

        # TODO: or use non-Pure PosicPath ?
        device_dir = PurePosixPath("/data/local/tmp/minicap-devel")
        r = device.perform_adb_cmd("shell mkdir {}".format(device_dir))
        print("R: ", r)
        minicap_path = minicap_root / "libs" / abi / bin
        minicap_so_base = minicap_root / "jni" / "minicap-shared" / "aosp" / "libs" / "android-{}" / abi / "minicap.so"
        minicap_so_path = Path(str(minicap_so_base).format(rel))
        if not minicap_so_path.exists():
            minicap_so_path = Path(str(minicap_so_base).format(sdk))
        p = device.perform_adb_cmd("push {} {}".format(minicap_path,
                                                       device_dir))
        print("P: ", p)
        p = device.perform_adb_cmd("push {} {}".format(minicap_so_path,
                                                       device_dir))
        print("P: ", p)
        start_cmd = "adb -s {id} shell LD_LIBRARY_PATH={dir} {dir}/{bin} {args}".format(
            id=device.adb_id, dir=device_dir, bin=bin, args=args)
        subprocess.Popen(
            shlex.split(start_cmd),
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL)
        print("Start CMD: ", start_cmd)
        print("Minicap: ", minicap_path)
        print("Minicap.so: ", minicap_so_path)
        print("Port: ", port)
        print("Rel: ", rel)
        device.perform_adb_cmd(
            "forward tcp:{} localabstract:minicap".format(port))
        return port

    def init_devices(self):
        adb_devices_result = perform_cmd("adb devices")
        devices = []
        for line in adb_devices_result.split("\n"):
            line = line.strip()
            if ("*" in line or "List of" in line or not line):
                continue
            adb_id, status = line.split("\t")
            device = device_record.init_mini(adb_id, status)
            device.android_version = device.get_property(PROP_ANDROID_VERSION)
            device.sdk_version = int(device.get_property(PROP_SDK_VERSION))
            device.device_name = device.get_property(PROP_DEVICE_NAME)
            print("Android: ", device.android_version)
            print("SDK: ", device.sdk_version)
            print("Name: ", device.device_name)
            device.minicap_port = self.launch_minicap(
                device, Path("~/sdk/openstf/minicap").expanduser())
            device.minitouch_port = self.launch_minitouch(
                device, Path("~/sdk/openstf/minitouch").expanduser())
            devices.append(device)


# TODO: should return a suitable provider as a singleton
# Maybe save it in Flask app globally?
def getProvider():
    pass


if __name__ == "__main__":
    provider = MiniDeviceProvider(1111, 1113)
    provider.init_devices()
