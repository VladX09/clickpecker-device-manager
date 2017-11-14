from .mini_provider import MiniDeviceProvider
from device_manager import utils

__mini_provider_instance = None


def get_provider():
    """Factory method, returning appropriate DeviceProvider according to configuration file

    Now it's only MINI configuration supported, which uses:
        OpenSTF Minicap: for obtainig device screenshot
        OpenSTF Minitouch: for sending multitouch commands
        ADB: for other commands

    """
    global __mini_provider_instance
    if __mini_provider_instance == None:
        config = utils.get_main_config()
        start_port = config.getint("Basic Config", "start_port")
        end_port = start_port + config.getint("Basic Config",
                                              "max_devices") * 2
        minicap_root = config.get("Basic Config", "minicap_root")
        minitouch_root = config.get("Basic Config", "minitouch_root")
        # logger.info("Start port: {}; End_port: {}".format(
        #     start_port, end_port))
        # logger.info("Minicap_root: {}; Minitouch_root: {}".format(
        #     minicap_root, minitouch_root))

        __mini_provider_instance = MiniDeviceProvider(
            start_port, end_port, minicap_root, minitouch_root)

    return __mini_provider_instance
