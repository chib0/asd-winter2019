"""
The thought server is basically a flask app, that handles REST api calls.
The request data are bson dicts. I could've used protobuf but then I wouldn't've had to work to keep this and sample
reader disjoint.

What's it gonna do?
The server generally just gets a message, writes it to the disk, and publishes a message that it has been received.
The message then goes into a parser that extrects logic info (like images), and puts it in files, republishes results
More and more parsers will see more and more messages as parsing takes place.
"""


from . import cortex_rest_server

def run_server(host, port, publish):
    cortex_rest_server.get_server()
