import subprocess
import shlex
import logging
from pathlib import Path, PurePosixPath

from device_manager.providers.device_provider import DeviceProvider
from device_manager.models.device import Device
from device_manager import utils
from device_manager.providers.ports_pool import PortsPool

# Add some constants for ADB
PROP_ANDROID_VERSION = "ro.build.version.release"
PROP_DEVICE_NAME = "ro.product.model"
PROP_SDK_VERSION = "ro.build.version.sdk"
PROP_ABI = "ro.product.cpu.abi"
PROP_PREVIEW = "ro.build.version.preview_sdk"

logger = logging.getLogger("device_manager.mini_provider")


class MiniDeviceProvider(DeviceProvider):
    def __init__(self, start_port, end_port, minicap_root, minitouch_root):
        self.ports_pool = PortsPool(start_port, end_port)
        self.minicap_root = Path(minicap_root).expanduser()
        self.minitouch_root = Path(minitouch_root).expanduser()
        self.devices = {}

    def launch_minitouch(self, device):

        # Check if minitouch was launched alraedy
        port = self._check_app(device, "minitouch", device.minitouch_port)
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

    def _check_app(self, device, name, port):
        app_running = device.check_app_running(name)
        port_exists = port is not None

        if app_running and port_exists:
            return port
        if app_running and not port_exists:
            device.kill_app("minicap")
        if not app_running and port_exists:
            self.ports_pool.release_port(port)
        return None

    def launch_minicap(self, device):

        # Check if minicap was launched alraedy
        port = self._check_app(device, "minicap", device.minicap_port)
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

    def _check_device_is_allowed(self, adb_id):
        whitelist = utils.get_whitelist_devices()
        blacklist = utils.get_blacklist_devices()

        if len(whitelist) > 0:
            return adb_id in whitelist

        if len(blacklist) > 0:
            return adb_id not in blacklist

        return True

    def _get_devices_from_adb(self):
        adb_devices_result = utils.perform_cmd("adb devices")
        devices = {}
        for line in adb_devices_result.split("\n"):
            line = line.strip()

            if ("*" in line or "List of" in line or not line):
                continue

            adb_id, status = line.split("\t")
            if not self._check_device_is_allowed(adb_id):
                continue

            if adb_id in self.devices:
                device = self.devices[adb_id]
            else:
                device = Device(adb_id=adb_id, status=status)
            logger.info("Handle device")
            device.android_version = device.get_property(PROP_ANDROID_VERSION)
            device.sdk_version = int(device.get_property(PROP_SDK_VERSION))
            device.device_name = device.get_property(PROP_DEVICE_NAME)
            device.minicap_port = self.launch_minicap(device)
            device.minitouch_port = self.launch_minitouch(device)
            devices[adb_id] = device

        logger.info("Collected Devices: {}".format(devices))
        return devices

    def _init_devices(self):
        logger.info(
            "Start devices (re)initialisation:\nWhitelist:{}\nBlacklist:{}".
            format(utils.get_whitelist_devices(), utils.get_blacklist_devices()))
        self.devices = self._get_devices_from_adb()
        return self.devices

    def _check_filter(self, device, key, value):
        if "__" not in key:
            key = key + "__eq"
        field_name, operator = key.split("__")
        field = getattr(device, field_name)

        if operator in ["eq", "lt", "gt", "le", "ge"]:
            operator = "__{}__".format(operator)
            result = getattr(field, operator)(value)
            if result is NotImplemented:
                raise TypeError("Wrong value type in filter: {}:{}".format(
                    key, value))
            return result

        if operator == "ne":
            result = not self._check_filter(device, field_name + "__eq", value)
            return result

        raise NotImplementedError(
            "Operator '{}' is not implemented".format(operator))

    def get_devices(self, filters=None):
        devices = self._init_devices().values()
        if filters is not None:
            for key, value in filters.items():
                devices = [
                    device for device in devices
                    if self._check_filter(device, key, value)
                ]
        devices = [device.copy() for device in devices]
        return devices

    def acquire_device(self, device):
        logger.info("Acquire device {}".format(device.adb_id))
        self.devices[device.adb_id].free = False

    def release_device(self, device):
        logger.info("Release device {}".format(device.adb_id))
        self.devices[device.adb_id].free = True
