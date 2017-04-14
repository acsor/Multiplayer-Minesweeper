#!/usr/bin/python3.2

from socket import *
from message import *
from concurrent.futures import Future, ThreadPoolExecutor
from argparse import ArgumentParser
from board import Board, State
from sys import argv


PROGRAM_NAME = "Minesweeper server"


class MineSweeperServer:
    HOST = ''
    PORT_DEFAULT = 3666
    LISTEN_BACKLOG = 0
    MAX_CLIENTS = 4

    def __init__(self, board, port=PORT_DEFAULT, debug=False):
        self.board = board
        self.debug = debug
        self.futures_to_connections = dict()

        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.HOST, port))
        self.server.listen(self.LISTEN_BACKLOG)

        self.executor = ThreadPoolExecutor(self.MAX_CLIENTS)
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
                    (len(self.futures_to_connections), self.MAX_CLIENTS)
                )
            return None
        else:
            connection = Connection(
                self.board,
                self.server.accept()[0],
                self.debug
            )
            future = self.executor.submit(connection)
            future.add_done_callback(self.make_shutdown_client())
            future.add_done_callback(self.make_auto_close())

            self.futures_to_connections[future] = connection

            return future, self.futures_to_connections[future]

    def is_full(self):
        return len(self.futures_to_connections) >= self.MAX_CLIENTS

    # Perhaps not the most elegant way to fix the argument passing of Future's add_done_callback(), but I expect
    # this closure to work, and this is what matters at the moment of this writing.
    # A future improvement may be something to consider.
    def make_shutdown_client(self):

        def shutdown_client(future):
            if future is not None:
                connection = self.futures_to_connections[future]

                if connection is not None:
                    connection.close()
                future.cancel()
                del self.futures_to_connections[future]

                if self.debug:
                    print("Connection closed: %d/%d still running" %
                          (len(self.futures_to_connections), self.MAX_CLIENTS))

        return shutdown_client

    def make_auto_close(self):

        def auto_close(future):
            if len(self.futures_to_connections) == 0:
                self.close()

        return auto_close


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

        # TO-DO Verify open() is being used correctly
        with open(self.client.fileno()) as stream:
            in_message = UTSMessage.parse_infer_type(stream.readline())

            while in_message is not None:
                if self.debug:
                    print("%s: %s" % (self.client, in_message))

                out_message = self._craft_out_from_in_message(UTSMessage.parse_infer_type(in_message))
                in_message = UTSMessage.parse_infer_type(stream.readline())

    def close(self):
        client_string = str(self.client)

        if self.client is not None:
            self.client.close()

        if self.debug:
            print("%s closed" % client_string)

    def _craft_out_from_in_message(self, in_message):
        result = None

        if isinstance(in_message, UTSLookMessage):
            pass
        elif isinstance(in_message, UTSDigMessage):
            pass
        elif isinstance(in_message, UTSFlagMessage):
            pass
        elif isinstance(in_message, UTSDeflagMessage):
            pass
        elif isinstance(in_message, UTSHelpRequestMessage):
            pass
        elif isinstance(in_message, UTSByeMessage):
            pass

        return result


def main():
    default_size, default_port = 10, MineSweeperServer.PORT_DEFAULT
    ap = ArgumentParser(PROGRAM_NAME)

    ap.add_argument("debug", action="store", help="Debug flag for server")
    ap.add_argument("-p", "--port", dest="port", type=int, action="store",
                    help="Local port where to connect the server")

    creation_group = ap.add_mutually_exclusive_group( )
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
        board = Board.create_from_probability(default_size)

    if arguments.port is not None:
        port = arguments.port
    else:
        port = default_port

    server = MineSweeperServer(board, port, arguments.debug)
    server.run_next_connection()

    while len(server.connections()) > 0:
        if not server.is_closed and not server.is_full():
            server.run_next_connection()

    del server

if __name__ == "__main__":
    main()
