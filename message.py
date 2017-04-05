#!/usr/bin/python3.2


class Message(object):

    def parse(self, raw_input):
        return self.message_factory(raw_input.strip())

    @staticmethod
    def message_factory(input_string):
        raise NotImplementedError()

    def get_representation(self):
        raise NotImplementedError()

    def __str__(self):
        return self.get_representation()


class UTSMessage(Message):
    """
    A UTSMessage (User-To-Server message) is a superclass for all those classes representing
    a message from the client to the server.
    """

    messages = (UTSLookMessage, UTSDigMessage, UTSFlagMessage, UTSDeflagMessage,
                UTSHelpRequestMessage, UTSByeMessage)

    def is_valid(self, board):
        # I'm still unsure what parameters this method should take. TO-DO Look forward this.
        raise NotImplementedError()


class UTSLookMessage(UTSMessage):
    REPR = "look"

    @staticmethod
    def message_factory(input_string):
        if input_string.endswith(UTSLookMessage.REPR, 0):
            return UTSLookMessage()
        else:
            raise ValueError("required \"%s\", found \"%s\"" %
                             (UTSLookMessage.REPR, input_string))

    def is_valid(self, board):
        return True

    def get_representation(self):
        return self.REPR


class UTSDigMessage(UTSMessage):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_valid(self, board):
        return (self.x, self.y) in board

class UTSFlagMessage(UTSMessage):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_valid(self, board):
        raise NotImplementedError()


class UTSDeflagMessage(UTSMessage):
    pass


class UTSHelpRequestMessage(UTSMessage):
    pass


class UTSByeMessage(UTSMessage):
    pass


class STUMessage(Message):
    """
    A STUMessage (Server-To-User message) is the counterpart of a USTMessage, and is any kind
    of message to be sent from the server to the user.
    """
    pass


class STUBoardMessage(STUMessage):
    pass


class STUBoomMessage(STUMessage):
    pass


class STUHelpMessage(STUMessage):
    pass


class STUHelloMessage(STUMessage):
    pass
