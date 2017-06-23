import unittest
import math
from minesweeper.utils import digits


class UncategorizedTest(unittest.TestCase):
    def test_digits(self):
        """
            Tests digits functions from minesweeper.utils
        """
        expected_output = {
            -(10 ** 5): 6, -1000: 4, -100: 3, -10: 2, -9: 1, -math.pi: 1, -1: 1, -0.5555: 1,
            0: 1, 0.5555: 1, 0.999999: 1, 10: 2, math.pi: 1, 15: 2, 20: 2, 49: 2, 80: 2, 99: 2, 100: 3, 101.40409: 3,
            999: 3, 1000: 4, 10 ** 5: 6, (10 ** 5) + 10: 6
        }

        for digit in expected_output.keys():
            self.assertEqual(
                digits(digit),
                expected_output[digit],
                "digits(%f) = %d" % (digit, digits(digit))
            )


if __name__ == "__main__":
    unittest.main()
