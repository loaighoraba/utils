from .adaptors import AdaptorFactory

def controller_send_a_message(json_params):
    phone_number = json_params['phone_number']
    message = json_params['message']
    
    adaptor = AdaptorFactory.get_adaptor()
    adaptor.send(phone_number, message)

    return "Message sent successfully"