import numpy as np
import base64

class Message(object):
    def __init__(self, name, data):
        self.name = name
        self.shape = data.shape
        self.dtype = str(data.dtype)
        self.data = data

    @classmethod
    def from_dict(cls, a_dict):
        data = base64.b64decode(a_dict["data"])
        data = np.frombuffer(data, dtype=a_dict['dtype'])
        if "shape" in a_dict:
            data = data.reshape(a_dict["shape"])
        return Message(a_dict.get("name", "data"), data)


    def as_dict(self):
        return {
            "name" : self.name,
            "shape" : self.shape,
            "dtype" : self.dtype,
            "data" : base64.b64encode(self.data)
        }