#!/usr/bin/python3.2


class Message(object):

    def get_representation(self):
        raise NotImplementedError()

    def __str__(self):
        return self.get_representation()


class UTSMessage(Message):
    """
    A UTSMessage (User-To-Server message) is a superclass for all those classes representing
    a message from the client to the server.
    """

    message_types = ()  # Assigned at the bottom of the file

    @classmethod
    def parse(cls, raw_input):
        return cls._message_factory(raw_input.strip())

    @staticmethod
    def parse_infer_type(raw_input):
        """
        Takes a raw_input string and returns the first concrete UTSMessage instance where raw_input
        was a valid string for static instantiation.

        :param raw_input: string to feed into a factory method.
        :return: object of a concrete UTSMessage class, or None if the method fails (e.g. raw_input is invalid).
        """
        result = None

        for i in UTSMessage.message_types:
            try:
                result = i.parse(raw_input)

                if result is not None:
                    break
            except Exception:
                continue

        # if result is None:
        #     raise ValueError(
        #         "\"%s\" couldn't be used to build an instance of any of the following classes:\n%s" %
        #         (raw_input, str(UTSMessage.message_types))
        #     )

        return result

    @classmethod
    def _message_factory(cls, factory_string):
        """
        Creates an instance of a concrete UTSMessage class by using a factory method.

        :param factory_string: string to construct a new object from.
        :return: a new instance whose class is a subtype of UTSMessage.
        """
        raise NotImplementedError()

    def is_valid(self, board):
        # I'm still unsure what parameters this method should take. TO-DO Look forward this.
        raise NotImplementedError()


class UTSLookMessage(UTSMessage):
    REPR = "look"

    @classmethod
    def _message_factory(cls, factory_string):
        if factory_string.endswith(UTSLookMessage.REPR, 0):
            return UTSLookMessage()
        else:
            raise ValueError("required \"%s\", found \"%s\"" %
                             (UTSLookMessage.REPR, factory_string))

    def is_valid(self, board):
        return True

    def get_representation(self):
        return self.REPR


class UTSDigMessage(UTSMessage):

    REPR_PREFIX = "dig"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def _message_factory(cls, factory_string):
        """
        Creates a new instance of UTSDigMessage from factory_string.

        :param factory_string: a string of the form "dig <space> [0-9]+ <space> [0-9]+". <space> refers to a single space only.
        :return: an UTSDigMessage instance created according to the method arguments.
        :raise: ValueError in case factory_string does not comply to the grammar.
        """
        components = factory_string.split(" ")
        x, y = int(components[1]), int(components[2])

        if cls.REPR_PREFIX != components[0]:
            raise ValueError("Expected %s, found %s" % (cls.REPR_PREFIX, components[0]))

        return UTSDigMessage(x, y)

    def is_valid(self, board):
        return (self.x, self.y) in board

    def get_representation(self):
        return "%s %d %d" % (self.REPR_PREFIX, self.x, self.y)


class UTSFlagMessage(UTSMessage):

    REPR_PREFIX = "flag"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def _message_factory(cls, factory_string):
        components = factory_string.split(" ")
        x, y = int(components[1]), int(components[2])

        if cls.REPR_PREFIX != components[0]:
            raise ValueError("Expected %s, found %s" % (cls.REPR_PREFIX, components[0]))

        return UTSFlagMessage(x, y)

    def get_representation(self):
        return "%s %d %d" % (self.REPR_PREFIX, self.x, self.y)

    def is_valid(self, board):
        return (self.x, self.y) in board


class UTSDeflagMessage(UTSMessage):

    REPR_PREFIX = "deflag"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def _message_factory(cls, factory_string):
        components = factory_string.split(" ")
        x, y = int(components[1]), int(components[2])

        if cls.REPR_PREFIX != components[0]:
            raise ValueError("Expected %s, found %s" % (cls.REPR_PREFIX, components[0]))

        return UTSDeflagMessage(x, y)

    def get_representation(self):
        return "%s %d %d" % (self.REPR_PREFIX, self.x, self.y)

    def is_valid(self, board):
        return (self.x, self.y) in board


class UTSHelpRequestMessage(UTSMessage):

    REPR = "help"

    @classmethod
    def _message_factory(cls, factory_string):
        if cls.REPR == factory_string:
            return UTSHelpRequestMessage()

    def is_valid(self, board):
        return True

    def get_representation(self):
        return self.REPR


class UTSByeMessage(UTSMessage):

    REPR = "bye"

    @classmethod
    def _message_factory(cls, factory_string):
        if cls.REPR == factory_string:
            return UTSByeMessage()
        else:
            raise ValueError("Expected %s, found %s" % (cls.REPR, factory_string))

    def is_valid(self, board):
        return True

    def get_representation(self):
        return self.REPR


class STUMessage(Message):
    """
    A STUMessage (Server-To-User message) is the counterpart of a USTMessage, and is any kind
    of message to be sent from the server to the user.
    """
    pass


class STUBoardMessage(STUMessage):
    def __init__(self, board):
        self.board = board

    def get_representation(self):
        return str(self.board)


class STUBoomMessage(STUMessage):

    REPR = "BOOM!"

    def get_representation(self):
        return self.REPR


class STUHelpMessage(STUMessage):
    # TO-DO Finish implementing this class
    REPR = """
    Function still not implemented
    """

    def get_representation(self):
        return self.REPR


class STUHelloMessage(STUMessage):
    # Decide what arguments the constructor of this class should take to know the number
    # of playing users.
    REPR = """
    Welcome to Minesweeper. An unknown number of people is playing including you.
    Type 'help' for help.
    """

    def get_representation(self):
        return self.REPR


UTSMessage.message_types = (UTSLookMessage, UTSDigMessage, UTSFlagMessage, UTSDeflagMessage,
                            UTSHelpRequestMessage, UTSByeMessage)
