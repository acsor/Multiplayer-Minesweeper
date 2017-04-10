#!/usr/bin/python3.2

import unittest
from minesweeper.server import MineSweeperServer, Connection


class ServerTest:

    def __init__(self):
        self.server = MineSweeperServer(None, debug=True)

    def test_default(self):
        self.server.run_next_connection()

        while len(self.server.futures_to_connections) > 0 and not self.server.is_closed:
            if not self.server.is_full():
                self.server.run_next_connection()

    def close(self):
        if self.server is not None:
            del self.server
        self.server = None

if __name__ == "__main__":
    s = ServerTest()

    s.test_default()
    s.close()
