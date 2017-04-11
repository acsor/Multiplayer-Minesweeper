import unittest
from unittest import TestCase
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
        b = Board(Board.DIFF_INTERMEDIATE)
        true_evaluations = [(0, 0), (0, b.width - 1), (b.height - 1, 0), (b.height - 1, b.width - 1),
                            (b.height // 2, b.width // 2)]
        false_evaluations = [(0, -1), (0, b.width), (b.height, 0), (b.height - 1, b.width)]

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
        b = Board(Board.DIFF_HARD)

        for s in b:
            if s.has_bomb:
                b.set_state(s.row, s.col, State.DUG)

        self.assertEqual(
            b.mines,
            str(b).count(Square.REPR_BOMB)
        )
        self.assertEqual(
            len(b) - b.mines,
            str(b).count(State.UNTOUCHED.representation)
        )

    def test_board_len(self):
        """
        Tests the length of a Board instance b when counting its number of squares, and when calculating
        b.height * b.width.
        """
        boards = [Board(Board.DIFF_INTERMEDIATE) for i in range(100)]

        for b in boards:
            self.assertEqual(
                b.height * b.width,
                len(b)
            )

def test_free():
    b = Board()

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
