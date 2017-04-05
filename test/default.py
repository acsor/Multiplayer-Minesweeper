#!/usr/bin/python3.2

import unittest
from message import *


class DefaultTest(unittest.TestCase):

    def testUSTLookMessage(self):
        try:
            UTSLookMessage.message_factory("look")
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
