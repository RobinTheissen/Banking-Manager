# Robin Theissen
class Customer:  # Customer Klasse
    def __init__(self, fName, lName, age, email, pw, bankingInst):
        self.pw = pw
        self.email = email
        self.age = age
        self.lName = lName
        self.fName = fName
        self.bankingInst = bankingInst
        self._data = [fName, lName, age, email, pw]
