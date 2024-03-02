import re


class TextValidator:
    @staticmethod
    def transaction_regex_validation(input_string):
        pattern = re.compile(r'[^\w\säöüß]+')
        return bool(pattern.search(input_string))

    @staticmethod
    def password_validation(password):
        (len(password) >= 8 and
         any(char.isupper() for char in password) and
         any(char.islower() for char in password) and
         any(char.isdigit() for char in password) and
         any(char in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`' for char in password) and
         password[0] not in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`' and
         password[-1] not in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`')
