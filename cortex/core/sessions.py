"""
The missions statement:
    Encapsulate all sessions into this file (might become a module)
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
what is a session?
    A session is a wrapper over a simple connection that can hold relevant state for it.
    There may be different kinds of connections, thus different kinds of sessions.

    There will generally be pairs of sessions, since connections are not symmetric. There's a client and a server.
    Therefore expect:
        A client->server session object
        A server->client sessions object

    These classes are generally coupled with the server/client and follow the protocol.
    The protocol messages, however, are defined in net_messages.proto.
"""

