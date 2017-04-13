import unittest
from unittest import TestCase, SkipTest
from random import randint
from minesweeper.board import *


class BoardTest(TestCase):

    def test_mines_distribution(self):
        empty, mined = randint(10, 100), randint(10, 100)
        distribution = Board._random_mines_distribution(empty, mined)

        self.assertEqual(
            len([i for i in distribution if not i]),
            empty
        )
        self.assertEqual(
            len([i for i in distribution if i]),
            mined
        )

    def test_contains(self):
        b = Board.from_difficulty(Board.DIFF_INTERMEDIATE)
        true_evaluations = [(0, 0), (0, b.width() - 1), (b.height() - 1, 0), (b.height() - 1, b.width() - 1),
                            (b.height() // 2, b.width() // 2)]
        false_evaluations = [(0, -1), (0, b.width()), (b.height(), 0), (b.height() - 1, b.width())]

        for i in true_evaluations:
            self.assertEqual(
                True,
                i in b,
            )

        for i in false_evaluations:
            self.assertEqual(
                False,
                i in b
            )

    def test_board_str(self):
        b = Board.from_difficulty(Board.DIFF_HARD)

        for s in b:
            if s.has_bomb:
                b.set_state(s.row, s.col, State.DUG)

        self.assertEqual(
            b.mines_count(),
            str(b).count(Square.REPR_BOMB)
        )
        self.assertEqual(
            len(b) - b.mines_count(),
            str(b).count(State.UNTOUCHED.representation)
        )

    def test_board_len(self):
        """
        Tests the length of a Board instance b when counting its number of squares, and when calculating
        diff[0] * diff[1] (namely, diff."height" * diff."width").
        """
        diff = Board.DIFF_INTERMEDIATE
        boards = [Board.from_difficulty(diff) for i in range(100)]

        for b in boards:
            self.assertEqual(
                diff[0] * diff[1],
                len(b)
            )

    def test_from_file(self):
        root = "./assets/"
        files = {
            "safe": ["board_6x6.ms", "board_8x8.ms"],
            "unsafe": ["board_invalid_6x6.ms", "board_invalid_6x7.ms", "board_invalid_7x7.ms"]
        }

        for file in files["safe"]:
            self.assertIsInstance(
                Board.from_file(root + file),
                Board
            )

        for file in files["unsafe"]:
            self.assertRaises(
                ValueError,
                Board.from_file,
                root + file
            )

def test_free():
    """
    Utily method to see some console output when debugging the code, as the unittest framework captures it and it didn't
    seem straightforward to me displaying it.
    """
    b = Board.from_difficulty()

    b.set_state(0, 1, State.DUG)
    b.set_state(3, 1, State.DUG)
    b.set_state(0, 2, State.DUG)
    b.set_state(0, 1, State.DUG)
    b.set_state(0, 5, State.DUG)
    b.set_state(6, 0, State.DUG)
    b.set_state(0, 8, State.DUG)
    b.set_state(1, 1, State.DUG)
    b.set_state(7, 2, State.DUG)
    b.set_state(4, 1, State.DUG)
    b.set_state(4, 3, State.FLAGGED)
    b.set_state(4, 5, State.FLAGGED)

    print(b)

if __name__ == "__main__":
    unittest.main(BoardTest)
