import json


_serializable_types = {}


def serializable(cls):
    assert hasattr(cls, "serialize"), f"{cls} has no serialize function"
    assert hasattr(cls, "deserialize"), f"{cls} has no deserialize function"
    _serializable_types[str(cls)] = cls
    return cls


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if (t := str(type(obj))) in _serializable_types:
            return {"_type": t, "value": obj.serialize()}
        return json.JSONEncoder.default(self, obj)


class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        self.old_object_hook = kwargs.get("object_hook", lambda x: x)
        kwargs["object_hook"] = self.object_hook
        json.JSONDecoder.__init__(self, *args, **kwargs)

    def object_hook(self, obj):
        if t := _serializable_types.get(obj.get("_type")):
            return t.deserialize(obj["value"])
        return self.old_object_hook(obj)


def setup(app):
    app.json_encoder = CustomJSONEncoder
    app.json_decoder = CustomJSONDecoder
