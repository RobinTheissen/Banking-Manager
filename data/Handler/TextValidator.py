import re


class TextValidator:
    @staticmethod
    def transaction_regex_validation(input_string):
        pattern = re.compile(r'[^\w\säöüß]+')
        return bool(pattern.search(input_string))

    @staticmethod
    def password_validation(password):
        conditions = [
            len(password) >= 8,
            any(char.isupper() for char in password),
            any(char.islower() for char in password),
            any(char.isdigit() for char in password),
            any(char in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`' for char in password),
            password[0] not in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`',
            password[-1] not in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`'
        ]

        return all(conditions)
