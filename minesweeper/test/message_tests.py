#!/usr/bin/python3.2

import unittest
from minesweeper.message import *


class UTSMessageTest(unittest.TestCase):

    def test_parse_infer_type(self):
        """
        Instantiates one object for every concrete subclass of UTSMessage using the type-inferring
        factory method parse_infer_type(), checking that the instance returned is of the expected
        type.
        """
        factory_strings = ("look", "dig 5 2", "flag 6 2", "deflag 3 6",
                           "help", "bye")
        message_classes = UTSMessage.message_types

        for string, mclass in zip(factory_strings, message_classes):
            o = UTSMessage.parse_infer_type(string)

            self.assertIsInstance(
                o,
                mclass
            )


if __name__ == "__main__":
    unittest.main()
