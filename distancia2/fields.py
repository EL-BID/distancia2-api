import json

import numpy as np
from django_mysql import models


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


class JSONField(models.JSONField):
    _default_json_encoder = NumpyEncoder(allow_nan=False)
