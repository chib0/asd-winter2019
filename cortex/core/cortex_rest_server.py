from flask import Flask, request

from cortex import utils
from cortex.utils import configuration
from utils.filesystem import MessageRecord


def get_logger():
    get_logger.counter += 1
    return utils.logging.get_logger(f'cortex_server_{get_logger.counter}')

get_logger.counter = 0


def get_server(publisher, server_name="cortex_api", *flask_args, **flask_kwargs):
    """
    Gets a server that accepts a thought and forwards it to the dispatcher.
    The server also gives configuration to users that request it.
    The server may support authentication given either SSL or checking cookies, it's not implemented.

    I am returning a Flask app without wrapping it because its functionality is good enough to not be wrapped.
    if I am to add servers later, they will be molded by this functionality ( which is run with a host and port,
     terminate when thread dies.)

    :param publisher: whatever pieplines the requests further down to the backend.
    :param server_name: ...
    :param flask_args: args to pass to the Flask constructor after the name. the name of this server is always 'api'
    :param flask_kwargs: kwargs to pass to the Flask constructor
    :return: the server to be 'run'
    """
    ThoughtAPI = Flask(server_name, *flask_args, **flask_kwargs)
    publish_func = publisher if callable(publisher) else publisher.publish
    @ThoughtAPI.route("/user/<id>", methods=["POST"])
    def handle_new_thought(id):
        """
        this handles a new thought on the user ID. if the user doesn't exits it should be created.
        :param id: the id from the url
        :return: empty string. this happens whether the backend manages to save the thought or not.
        """
        with MessageRecord.create() as mr:
            mr.write(request.data)
            message = dict(user=id, snapshot=mr.uri)

        publish_func(configuration.topics.snapshot, message)
        return ''

    @ThoughtAPI.route("/configuration")
    def get_configuration():
        return configuration.get_config()[configuration.CONFIG_CLIENT_CONFIG]


    return ThoughtAPI

