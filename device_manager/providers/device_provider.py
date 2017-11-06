class DeviceProvider:
    """Provider interface. Just to make a clear convention
    TODO: use zope.interface to make it strict?
    """

    def get_devices(self, filters=None):
        raise NotImplementedError(
            "get_devices() not implemented by DeviceProvider class")

def get_provider():
    """Factory method, returning appropriate DeviceProvider according to configuration file

    Now it's only MINI configuration supported, which uses:
        OpenSTF Minicap: for obtainig device screenshot
        OpenSTF Minitouch: for sending multitouch commands
        ADB: for other commands

    """

    config = utils.get_main_config()
    start_port = config.getint("Basic Config", "start_port")
    end_port = start_port + config.getint("Basic Config", "max_devices") * 2
    minicap_root = config.get("Basic Config", "minicap_root")
    minitouch_root = config.get("Basic Config", "minitouch_root")
    logger.info("Start port: {}; End_port: {}".format(start_port, end_port))
    logger.info("Minicap_root: {}; Minitouch_root: {}".format(
        minicap_root, minitouch_root))

    return providers.mini_provider.MiniDeviceProvider(start_port, end_port, minicap_root,
                              minitouch_root)
