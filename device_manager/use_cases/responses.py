class ResponseSuccess(object):
    SUCCESS = 'SUCCESS'

    def __init__(self, value=None):
        self.type = self.SUCCESS
        self.value = value

    def successfull(self):
        return True


class ResponseFailure(object):
    RESOURCE_ERROR = 'RESOURCE_ERROR'
    PARAMETERS_ERROR = 'PARAMETERS_ERROR'
    SYSTEM_ERROR = 'SYSTEM_ERROR'

    def __init__(self, type_, cause):
        self.type = type_
        self.message = self._format_message(cause)

    def _format_message(self, cause):
        if isinstance(cause, Exception):
            return "{}: {}".format(cause.__class__.__name__, cause)
        return "{}".format(cause)

    def successfull(self):
        return False

    @property
    def value(self):
        return {'type': self.type, 'message': self.message}

    @classmethod
    def resource_error(cls, message=None):
        return cls(cls.RESOURCE_ERROR, message)

    @classmethod
    def system_error(cls, message=None):
        return cls(cls.SYSTEM_ERROR, message)

    @classmethod
    def parameters_error(cls, message=None):
        return cls(cls.PARAMETERS_ERROR, message)

    @classmethod
    def invalid_request(cls, invalid_request_object):
        message = "\n".join([
            "{}: {}".format(err['parameter'], err['message'])
            for err in invalid_request_object.errors
        ])
        return cls.parameters_error(message)
