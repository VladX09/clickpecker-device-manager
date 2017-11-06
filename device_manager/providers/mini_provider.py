import subprocess
import shlex
import logging
from pathlib import Path, PurePosixPath

from device_manager.providers.device_provider import DeviceProvider
from device_manager.models import device
from device_manager import utils

# Add some constants for ADB
PROP_ANDROID_VERSION = "ro.build.version.release"
PROP_DEVICE_NAME = "ro.product.model"
PROP_SDK_VERSION = "ro.build.version.sdk"
PROP_ABI = "ro.product.cpu.abi"
PROP_PREVIEW = "ro.build.version.preview_sdk"

logger = logging.getLogger("device_manager.mini_provider")


class MiniDeviceProvider(DeviceProvider):
    def __init__(self, start_port, end_port, minicap_root, minitouch_root):
        self.ports_pool = configuration.PortsPool(start_port, end_port)
        self.minicap_root = Path(minicap_root).expanduser()
        self.minitouch_root = Path(minitouch_root).expanduser()
        self.devices = {}

    def launch_minitouch(self, device):

        # Check if minitouch was launched alraedy
        port = self.check_app(device, "minitouch")
        if port is not None:
            return port

    # Get device's properties to choose right minitouch executable
        abi = device.get_property(PROP_ABI)
        if device.sdk_version >= 16:
            bin = "minitouch"
        else:
            bin = "minitouch-nopie"

        # Prepare all necessary paths
        minitouch_path = self.minitouch_root / "libs" / abi / bin
        device_dir = PurePosixPath("/data/local/tmp")

        # Push minitouch executable to device
        device.perform_adb_cmd("push {} {}".format(minitouch_path, device_dir))

        # Launch minitouch
        start_cmd = "adb -s {id} shell {path}".format(
            id=device.adb_id, path=device_dir / bin)
        subprocess.Popen(
            shlex.split(start_cmd),
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL)

        # Forward minitouch tcp port
        port = self.ports_pool.get_port()
        device.perform_adb_cmd(
            "forward tcp:{} localabstract:minitouch".format(port))
        return port

    def check_app(self, device, name):
        app_running = device.check_app_running("minicap")
        port_exists = device.minicap_port is not None

        if app_running and port_exists:
            return device.minicap_port
        if app_running and not port_exists:
            device.kill_app("minicap")
        if not app_running and port_exists:
            self.ports_pool.release_port(device.minicap_port)
        return None

    def launch_minicap(self, device):

        # Check if minicap was launched alraedy
        port = self.check_app(device, "minicap")
        if port is not None:
            return port

        # Get device's properties to choose right minicap executable
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

        # Configure real and virtual screen size
        size = device.get_screen_size()
        args = "-P {}@{}/0".format(size, size)

        # Prepare all necessary paths
        device_dir = PurePosixPath("/data/local/tmp/minicap-devel")
        minicap_path = self.minicap_root / "libs" / abi / bin
        minicap_so_base = self.minicap_root / "jni" / "minicap-shared" / "aosp" / "libs" / "android-{}" / abi / "minicap.so"
        minicap_so_path = Path(str(minicap_so_base).format(rel))
        if not minicap_so_path.exists():
            minicap_so_path = Path(str(minicap_so_base).format(sdk))
        logger.debug("Device: {}; Paths: {},{} -> {}".format(
            device.adb_id, minicap_path, minicap_so_path, device_dir))

        # Push minicap executable to device
        device.perform_adb_cmd("shell mkdir {}".format(device_dir))
        device.perform_adb_cmd("push {} {}".format(minicap_path, device_dir))
        device.perform_adb_cmd("push {} {}".format(minicap_so_path,
                                                   device_dir))
        # Launch minicap
        start_cmd = "adb -s {id} shell LD_LIBRARY_PATH={dir} {dir}/{bin} {args}".format(
            id=device.adb_id, dir=device_dir, bin=bin, args=args)
        logger.debug("Device: {} starting; Start_cmd: '{}'".format(
            device.adb_id, start_cmd))

        subprocess.Popen(
            shlex.split(start_cmd),
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL)

        # Forward minicap tcp port
        # TODO: add Pool's KeyError handler
        port = self.ports_pool.get_port()
        device.perform_adb_cmd(
            "forward tcp:{} localabstract:minicap".format(port))
        return port

    def init_devices(self):
        adb_devices_result = utils.perform_cmd("adb devices")
        _devices = {}
        for line in adb_devices_result.split("\n"):
            line = line.strip()
            if ("*" in line or "List of" in line or not line):
                continue
            adb_id, status = line.split("\t")

            if adb_id in self.devices:
                device = self.devices[adb_id]
            else:
                device = device.Device(adb_id=adb_id, status=status)
            device.android_version = device.get_property(PROP_ANDROID_VERSION)
            device.sdk_version = int(device.get_property(PROP_SDK_VERSION))
            device.device_name = device.get_property(PROP_DEVICE_NAME)
            device.minicap_port = self.launch_minicap(device)
            device.minitouch_port = self.launch_minitouch(device)
            _devices[adb_id] = device
        self.devices = _devices
        return _devices

    def _check_filter(self, device, key, value):
        if "__" not in key:
            key = key + "__eq"
        key, operator = key.split("__")
        field = getattr(device, key)

        if operator in ["eq", "lt", "gt", "le", "ge"]:
            operator = "__{}__".format(operator)
            return getattr(field, operator)(value)

    def get_devices(self, filters=None):
        devices = self.init_devices()
        if filters is not None:
            for key, value in filters.items():
                devices = [
                    device for device in devices
                    if self._check_filter(device, key, value)
                ]
        return devices