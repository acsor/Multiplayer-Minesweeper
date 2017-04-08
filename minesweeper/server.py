#!/usr/bin/python3.2

from socket import *
from minesweeper.message import *


class MineSweeperServer:
    HOST = ''
    PORT = 3666
    LISTEN_BACKLOG = 1

    def __init__(self, port=PORT, debug=False):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.debug = debug
        self.clients = list()
        self.server.bind((self.HOST, port))
        self.server.listen(self.LISTEN_BACKLOG)

        if debug:
            print("Listening at port %d..." % port)

    def __del__(self):
        self.server.close()

    def next_client(self):
        self.clients.append(self.server.accept())


class Connection:

    def __init__(self, board, client, debug=False):
        self.board = board
        self.client = client
        self.debug = debug

    def __del__(self):
        if self.client is not None:
            self.client.close()

    def handle_connection(self):
        if self.debug:
            address = self.client.getpeername()
            print("Handling %s:%s" % (address[0], address[1]))

        # TO-DO Verify open() is being used correctly
        with open(self.client.fileno()) as stream:
            in_message = UTSMessage.parse_infer_type(stream.readline())

            while in_message is not None:
                out_message = self._craft_out_from_in_message(UTSMessage.parse_infer_type(in_message))
                in_message = UTSMessage.parse_infer_type(stream.readline())

        self.client.close()

    def _craft_out_from_in_message(self, in_message):
        result = None

        # TO-DO Check this use of type() works as expected
        if type(in_message) is UTSLookMessage:
            pass
        elif type(in_message) is UTSDigMessage:
            pass
        elif type(in_message) is UTSFlagMessage:
            pass
        elif type(in_message) is UTSDeflagMessage:
            pass
        elif type(in_message) is UTSHelpRequestMessage:
            pass
        elif type(in_message) is UTSByeMessage:
            pass

        return result

if __name__ == "__main__":
    print("Hello, I'm working!")
