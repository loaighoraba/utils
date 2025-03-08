"""classes simulating libraries that send messages using different APIs
"""

class Vodafone:
    def __init__(self, api_key):
        self.api_key = api_key

    def send_vodafone_message(self, phone_number, message):
        print(f"Sending {message} to {phone_number} using Vodafone API")


class Orange:
    def __init__(self, api_key):
        self.api_key = api_key

    # note: the method name is different from the Vodafone class
    # note: the method parameters order is different from the Vodafone class
    def send_orange_message(self, message, phone_number):
        print(f"Sending {message} to {phone_number} using Orange API")


class We:
    def __init__(self, api_key):
        self.api_key = api_key

    def send_we_message(self, phone_number, message, some_other_parameter):
        print(
            f"Sending {message} to {phone_number} with another parameter {some_other_parameter} using We API")