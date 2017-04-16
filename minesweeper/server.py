from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from socket import *
from sys import argv
from functools import partial

from minesweeper.board import Board, State
from minesweeper.message import *


class MineSweeperServer:

    DEFAULTS = {
        "host": '',
        "port": 3666,
        "listen_backlog": 0,
        "max_clients": 4
    }

    def __init__(self, board, port=DEFAULTS["port"], debug=False):
        self.board = board
        self.debug = debug
        self.futures_to_connections = dict()

        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.DEFAULTS["host"], port))
        self.server.listen(self.DEFAULTS["listen_backlog"])

        self.executor = ThreadPoolExecutor(self.DEFAULTS["max_clients"])
        self.is_closed = False

        # TO-DO Replace print statements with more appropriate log primitives for debugging
        if debug:
            print("Listening at port %d..." % port)

    def __repr__(self):
        repr_unknown = "unknown"

        if not self.is_closed:
            host = self.server.getsockname()[0] or repr_unknown
            port = self.server.getsockname()[1] or repr_unknown
        else:
            host = port = repr_unknown

        return "<'%s.%s' object, host=%s, port=%s, debug=%s>" %\
               (MineSweeperServer.__module__, self.__class__.__name__, host, port, self.debug)

    def __del__(self):
        if not self.is_closed:
            self.close()

    def close(self):
        self.executor.shutdown(False)

        self.server.shutdown(SHUT_RDWR)
        self.server.detach()
        self.server.close()
        del self.server

        self.is_closed = True

        if self.debug:
            print(repr(self))

    def connections(self):
        return self.futures_to_connections.values()

    def run_next_connection(self):
        # The block of code below may be deleted, as ThreadPoolExecutor's constructor supports
        # specifying the number of max worker threads. TO-DO Delete the block below, if it isn't
        # needed.
        if self.is_full():
            if self.debug:
                print(
                    "Reached maximum number of connections: %d/%d occupied" %
                    (len(self.futures_to_connections), self.DEFAULTS["max_clients"])
                )
            return None
        else:
            connection = Connection(
                self.board,
                self.server.accept()[0],
                self.debug
            )
            future = self.executor.submit(connection)
            future.add_done_callback(self._make_callback_shutdown_client())

            self.futures_to_connections[future] = connection

            return future, self.futures_to_connections[future]

    def is_full(self):
        return len(self.futures_to_connections) >= self.DEFAULTS["max_clients"]

    def _make_callback_shutdown_client(self):

        def _callback_shutdown_client(future):
            connection = self.futures_to_connections[future]

            if not connection.debug:
                connection.close()
                future.cancel()
                self.futures_to_connections.pop(future)

            if self.debug:
                print("Connection closed: %d/%d still running" %
                      (len(self.futures_to_connections), self.DEFAULTS["max_clients"]))

        return _callback_shutdown_client

class Connection:

    def __init__(self, board, client, debug=False):
        self.board = board
        self.client = client
        self.debug = debug

    def __repr__(self):
        return repr(self.client)

    def __del__(self):
        self.close()

    def __call__(self, *args, **kwargs):
        return self.start()

    def start(self):
        if self.debug:
            print("%s:%s connected" % self.client.getpeername())

        self.client.send(STUHelloMessage(-1).get_representation().encode())

        # TO-DO Verify open() is being used correctly
        with open(self.client.fileno()) as stream:
            in_message = UTSMessage.parse_infer_type(stream.readline())

            while in_message is not None:
                if self.debug:
                    print("%s: %s" % (self.client, in_message))

                out_message = self._process_in_message(in_message)
                self.client.send(out_message.get_representation().encode())

                if isinstance(out_message, STUBoomMessage):
                    in_message = None
                elif isinstance(out_message, STUByemessage):
                    in_message = None
                else:
                    in_message = UTSMessage.parse_infer_type(stream.readline())

    def close(self):
        client_string = str(self.client)

        if self.client is not None:
            self.client.close()

        if self.debug:
            print("%s closed" % client_string)

    def _process_in_message(self, in_message):
        result = None

        if isinstance(in_message, UTSLookMessage):
            result = STUBoardMessage(self.board)
        elif isinstance(in_message, UTSDigMessage):
            error = in_message.find_errors(self.board)

            if error is None:
                self.board.set_state(in_message.row, in_message.col, State.DUG)
                square = self.board.square(in_message.row, in_message.col)

                if square.has_bomb:
                    square.has_bomb = False
                    result = STUBoomMessage()
                else:
                    result = STUBoardMessage(self.board)
            else:
                result = STUErrorMessage(error)
        elif isinstance(in_message, UTSFlagMessage):
            self.board.set_state(in_message.row, in_message.col, State.FLAGGED)
            result = STUBoardMessage(self.board)
        elif isinstance(in_message, UTSDeflagMessage):
            square = self.board.square(in_message.row, in_message.col)

            if square.state == State.FLAGGED:
                self.board.set_state(in_message.row, in_message.col, State.UNTOUCHED)

            result = STUBoardMessage(self.board)
        elif isinstance(in_message, UTSHelpRequestMessage):
            result = STUHelpMessage()
        elif isinstance(in_message, UTSByeMessage):
            result = STUByemessage(self.debug)

        return result


def main():
    defaults = {
        "size": 10,
        "port": MineSweeperServer.DEFAULTS["port"],
        "program_name": "Minesweeper server",
    }
    ap = ArgumentParser(defaults["program_name"])

    ap.add_argument("debug", action="store", help="Debug flag for server")
    ap.add_argument("-p", "--port", dest="port", type=int, action="store",
                    help="Local port where to connect the server")

    creation_group = ap.add_mutually_exclusive_group()
    creation_group.add_argument("-s", "--size", dest="size", action="store", type=int,
                                help="Value of the height and width of the grid")
    creation_group.add_argument("-f", "--file", dest="file", action="store", type=str,
                                help="Path pointing to a board file")

    arguments = ap.parse_args(argv[1:])

    if arguments.size is not None:
        board = Board.create_from_probability(arguments.size, arguments.size)
    elif arguments.file is not None:
        board = Board.create_from_file(arguments.file)
    else:
        board = Board.create_from_probability(defaults["size"], defaults["size"])

    if arguments.port is not None:
        port = arguments.port
    else:
        port = defaults["port"]

    server = MineSweeperServer(board, port, arguments.debug)
    server.run_next_connection()

    while len(server.connections()) > 0:
        if not server.is_closed and not server.is_full():
            server.run_next_connection()

    server.close()

if __name__ == "__main__":
    main()
