class DeviceProvider:
    """Provider interface. Just to make a clear convention
    TODO: use zope.interface to make it strict?
    """

    def get_devices(self, filters=None):
        raise NotImplementedError(
            "get_devices() not implemented by DeviceProvider class")
