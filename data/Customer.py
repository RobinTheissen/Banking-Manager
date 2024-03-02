import json
from json import JSONEncoder


class Customer:
    def __init__(self, fName, lName, age, email, pw, bankingInst):
        self.pw = pw
        self.email = email
        self.age = age
        self.lName = lName
        self.fName = fName
        self.bankingInst = bankingInst
        self._data = [fName, lName, age, email, pw]

    def __iter__(self):
        for elem in self._data:
            yield elem

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @property
    def data(self):
        return self._data


# subclass JSONEncoder
class CustomerEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
