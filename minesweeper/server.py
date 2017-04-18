import sys
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from logging import *
from socket import *
from sys import argv

from minesweeper.board import Board, State
from minesweeper.message import *
from minesweeper.utils import is_boolean


class MineSweeperServer:

    DEFAULT_CONFIGS = {
        "host": '',
        "port": 3666,
        "listen_backlog": 0,
        "max_clients": 4
    }

    def __init__(self, board, port=DEFAULT_CONFIGS["port"], debug=False):
        self.board = board
        self.futures_to_connections = dict()

        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.DEFAULT_CONFIGS["host"], port))
        self.server.listen(self.DEFAULT_CONFIGS["listen_backlog"])

        self.executor = ThreadPoolExecutor(self.DEFAULT_CONFIGS["max_clients"])
        self.is_closed = False

        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(StreamHandler(sys.stdout) if debug else NullHandler())

        self.logger.debug("Listening at port %d...", port)

    def __repr__(self):
        repr_unknown = "unknown"

        if not self.is_closed:
            host = self.server.getsockname()[0] or repr_unknown
            port = self.server.getsockname()[1] or repr_unknown
        else:
            host = port = repr_unknown

        return "<'%s.%s' object, host=%s, port=%s, debug=%s>" %\
               (MineSweeperServer.__module__, self.__class__.__name__, host, port, self.is_debug_active())

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

        self.logger.debug(repr(self))

    def connections(self):
        return self.futures_to_connections.values()

    def run_next_connection(self):
        # The block of code below may be deleted, as ThreadPoolExecutor's constructor supports
        # specifying the number of max worker threads. TO-DO Delete the block below, if it isn't
        # needed.
        if self.is_full():
            self.logger.debug(
                "Reached maximum number of connections: %d/%d occupied",
                len(self.futures_to_connections), self.DEFAULT_CONFIGS["max_clients"]
            )
            return None
        else:
            connection = Connection(
                self.board,
                self.server.accept()[0],
                self.is_debug_active()
            )
            future = self.executor.submit(connection)
            future.add_done_callback(self._make_callback_shutdown_client())

            self.futures_to_connections[future] = connection

            return future, self.futures_to_connections[future]

    def is_full(self):
        return len(self.futures_to_connections) >= self.DEFAULT_CONFIGS["max_clients"]

    def is_debug_active(self):
        return NullHandler not in (type(h) for h in self.logger.handlers)

    def _make_callback_shutdown_client(self):

        def _callback_shutdown_client(future):
            connection = self.futures_to_connections[future]

            if not connection.is_debug_active():
                connection.close()
                future.cancel()
                self.futures_to_connections.pop(future)

            self.logger.debug(
                "Connection closed: %d/%d still running",
                len(self.futures_to_connections),
                self.DEFAULT_CONFIGS["max_clients"]
            )

        return _callback_shutdown_client


class Connection:

    def __init__(self, board, client, debug=False):
        self.board = board
        self.client = client
        self.logger = getLogger(__name__)

    def __repr__(self):
        return repr(self.client)

    def __del__(self):
        self.close()

    def __call__(self, *args, **kwargs):
        return self.start()

    def start(self):
        self.logger.debug("%s:%s connected", *self.client.getpeername())

        self.client.send(STUHelloMessage(-1).get_representation().encode())

        # TO-DO Verify open() is being used correctly
        with open(self.client.fileno()) as stream:
            in_message = UTSMessage.parse_infer_type(stream.readline())

            while in_message is not None:
                self.logger.debug("%s:%s: %s", *self.client.getpeername(), in_message)

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

        self.logger.debug("%s closed", client_string)

    def is_debug_active(self):
        return NullHandler not in (type(h) for h in self.logger.handlers)

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
            result = STUByemessage(self.is_debug_active())

        return result


def main():
    defaults = {
        "size": 10,
        "port": MineSweeperServer.DEFAULT_CONFIGS["port"],
        "program_name": "Minesweeper server",
    }
    ap = ArgumentParser(defaults["program_name"])

    ap.add_argument("-d", "--debug", dest="debug", action="store", type=is_boolean,
                    required=True, help="Debug flag for server")
    ap.add_argument("-p", "--port", dest="port", action="store", type=int,
                    default=defaults["port"], help="Local port where to connect the server")

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

    server = MineSweeperServer(board, arguments.port, arguments.debug)
    server.run_next_connection()

    while len(server.connections()) > 0:
        if not server.is_closed and not server.is_full():
            server.run_next_connection()

    server.close()

if __name__ == "__main__":
    main()
