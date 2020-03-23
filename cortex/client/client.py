from socket import socket
import datetime
from cortex.core.thought import Thought
from cortex.utils import ProtobufConnection
from cortex.core import net_messages_pb2


class ClientServerSession(ProtobufConnection):
    """
    This implements a session between a client and a server, from the client side.
    """
    def __init__(self, socket, /, server_config=None):
        """
        initialize the session
        :param socket: a connected socket
        :param server_config: for testing / server configuration
        """
        super().__init__(socket)
        self.config = server_config

    def perform_handshake(self, user_info):
        """
        completes the handshake with the server, attaining configuration from the server.
        fails on connection failures.
        :param user_info: the information regarding a user. may be auth data in the end lol
        """
        ci_message = net_messages_pb2.ClientInfo(id=user_info.id,
                                                 name=user_info.name,
                                                 birth_date_seconds=user_info.date_of_birth)
        self.send(ci_message)
        self.config = self.receive(net_messages_pb2.ServerConfig)


    def send_thought(self, thought):
        """
        sends the given thought in a manner that the server asked for
        :param thought: a thought. has to support to_snapshot
        """
        self.send_message(thought.to_snapshot())



def upload_thought(address, user_info, thought):
    """
     uploads a fully constructed thought to the server
    """
    address, port = address[0], int(address[1])
    with ClientServerSession.connect(address, port) as session:
        session.perform_handshake(user_info)
        session.send_thought(thought)



