import subprocess
import shlex
import configuration
import device_record
import json
import logging
from logging import config
from pathlib import Path, PurePosixPath

# Configure and add module-level logger
with open("logger.json") as f:
    conf = json.load(f)
logging.config.dictConfig(conf)
logger = logging.getLogger("device_manager")

# Add some constants for ADB
PROP_ANDROID_VERSION = "ro.build.version.release"
PROP_DEVICE_NAME = "ro.product.model"
PROP_SDK_VERSION = "ro.build.version.sdk"
PROP_ABI = "ro.product.cpu.abi"
PROP_PREVIEW = "ro.build.version.preview_sdk"


class DeviceProvider:
    """Provider interface. Just to make a clear convention
    TODO: use zope.interface to make it strict?
    """

    def get_device_by_spec(self, json_spec):
        pass

    def get_device_list(self):
        pass


class MiniDeviceProvider(DeviceProvider):
    def __init__(self, start_port, end_port, minicap_root, minitouch_root):
        self.ports_pool = configuration.PortsPool(start_port, end_port)
        self.minicap_root = Path(minicap_root).expanduser()
        self.minitouch_root = Path(minitouch_root).expanduser()

    def launch_minitouch(self, device):

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

    def launch_minicap(self, device):

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
        adb_devices_result = device_record.perform_cmd("adb devices")
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
            device.minicap_port = self.launch_minicap(device)
            device.minitouch_port = self.launch_minitouch(device)
            devices.append(device)
        # TODO: add {logger.info(device.to_json()) for device in devices}
        return devices


# TODO: should return a suitable provider as a singleton
# Maybe save it in Flask app globally?
def getProvider():
    """Factory method, returning appropriate DeviceProvider according to configuration file

    Now it's only MINI configuration supported, which uses:
        OpenSTF Minicap: for obtainig device screenshot
        OpenSTF Minitouch: for sending multitouch commands
        ADB: for other commands

    """

    config = configuration.get_main_config()
    start_port = config.getint("Basic Config", "start_port")
    end_port = start_port + config.getint("Basic Config", "max_devices") * 2
    minicap_root = config.get("Basic Config", "minicap_root")
    minitouch_root = config.get("Basic Config", "minitouch_root")
    logger.info("Start port: {}; End_port: {}".format(start_port, end_port))
    logger.info("Minicap_root: {}; Minitouch_root: {}".format(
        minicap_root, minitouch_root))

    return MiniDeviceProvider(start_port, end_port, minicap_root,
                              minitouch_root)


if __name__ == "__main__":
    provider = getProvider()
    provider.init_devices()
