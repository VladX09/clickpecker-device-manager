import collections


class ValidRequest(object):
    @classmethod
    def from_dict(cls, dict_):
        raise NotImplementedError

    def valid(self):
        return True


class InvalidRequest(object):
    def __init__(self):
        self.errors = []

    def add_error(self, parameter, message):
        self.errors.append({'parameter': parameter, 'message': message})

    def has_errors(self):
        return len(self.errors) > 0

    def valid(self):
        return False


class DeviceObtainRequest(ValidRequest):
    def __init__(self, filters=None):
        self.filters = filters

    @classmethod
    def from_dict(cls, dict_):
        invalid_req = InvalidRequest()

        if 'filters' in dict_ and not isinstance(dict_['filters'],
                                                 collections.Mapping):
            invalid_req.add_error('filters', 'is not a {}'.format(
                collections.Mapping))

        if invalid_req.has_errors():
            return invalid_req

        return DeviceObtainRequest(filters=dict_.get('filters', None))
