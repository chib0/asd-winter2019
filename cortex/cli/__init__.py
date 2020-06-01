from . import api_consumer

def get_consumer(host, port ):
    return api_consumer.Consumer(host, port)
