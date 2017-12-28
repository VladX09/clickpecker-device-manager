import json

class DeviceEncoder(json.JSONEncoder):
    def default(self,o):
        return o.to_dict()
