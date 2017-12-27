import collections
from packaging import version


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
    def from_dict(cls, data):
        invalid_req = InvalidRequest()

        if 'filters' in data and not isinstance(data['filters'],
                                                 collections.Mapping):
            invalid_req.add_error('filters', 'is not a {}'.format(
                collections.Mapping))

        if invalid_req.has_errors():
            return invalid_req

        filters = data.get('filters', None)
        if filters is not None:
            filters = DeviceObtainRequest.format_filters(filters)

        return DeviceObtainRequest(filters)

    @staticmethod
    def format_filters(original_filters):
        formatted_filters = dict(original_filters)
        for k,v in original_filters.items():
            if "android_version" in k:
                formatted_filters[k] = version.parse(v)
        return formatted_filters
