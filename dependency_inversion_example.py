##### BEGIN FILE libraries.py #####
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

##### END OF FILE adaptors.py #####

##### BEGIN FILE adaptors.py #####

""""
notes:
    - all adaptors have the same method signature: send(phone_number, message)
    - each adaptor uses the corresponding API special method to send the message
"""

#from libraries import Orange, Vodafone, We

class VodafoneAdaptor:
    def __init__(self, api_key):
        self.api_key = api_key

    def send(self, phone_number, message):
        # Send message using Vodafone API
        Vodafone(self.api_key).send_vodafone_message(phone_number, message)


class OrangeAdaptor:
    def __init__(self, api_key):
        self.api_key = api_key

    def send(self, phone_number, message):
        # Send message using Orange API
        Orange(self.api_key).send_orange_message(message, phone_number)


class WeAdaptor:
    def __init__(self, api_key):
        self.api_key = api_key

    def send(self, phone_number, message):
        # Send message using We API
        # Note: We API requires an additional parameter
        We(self.api_key).send_we_message(
            phone_number, message, "some_other_parameter")


class AdaptorFactory:
    # this is the only place which you will change when
    # you want to change the API library, normall you will get this
    # from a configuration file, not hard coded like this
    config = {
        "api_name": "vodafone",
        "api_key": "1234"
    }

    @staticmethod
    def get_adaptor():
        api_key = AdaptorFactory.config["api_key"]
        api_name = AdaptorFactory.config["api_name"]

        if api_name == "vodafone":
            return VodafoneAdaptor(api_key)
        if api_name == "orange":
            return OrangeAdaptor(api_key)
        if api_name == "we":
            return WeAdaptor(api_key)
        raise ValueError(f"API {api_name} not supported")

##### END OF FILE adaptors.py #####

##### BEGIN FILE controller.py #####

# from adaptors import AdaptorFactory

def controller_send_a_message(json_params):
    phone_number = json_params['phone_number']
    message = json_params['message']
    
    adaptor = AdaptorFactory.get_adaptor()
    adaptor.send(phone_number, message)

    return "Message sent successfully"

##### END OF FILE controller.py #####