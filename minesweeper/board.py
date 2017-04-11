#!/usr/bin/python3.2

from enum import Enum, unique
from random import shuffle


@unique
class State(Enum):
    UNTOUCHED = "-"
    FLAGGED = "F"
    DUG = " "

    def __init__(self, representation):
        self.representation = representation


class Square:
    def __init__(self, x, y, has_bomb, state):
        self.x, self.y = x, y
        self.has_bomb = has_bomb
        self.state = state

    def __repr__(self):
        return "<%s.%s object, x=%d, y=%d, has_bomb=%s, state=%s>" % \
               (self.__class__.__module__, self.__class__.__name__, self.x, self.y,
                self.has_bomb, self.state.name)

    def __str__(self):
        return self.state.representation


class Board:
    # Height, width, mines number
    DIFF_EASY = (9, 9, 10)
    DIFF_INTERMEDIATE = (16, 16, 40)
    DIFF_HARD = (16, 30, 99)

    def __init__(self, difficulty=DIFF_EASY):
        self.height, self.width, self.mines = difficulty
        self.squares = list()
        mines_distribution = Board._random_mines_distribution(
            (self.height * self.width) - self.mines,
            self.mines
        )

        for row in range(self.height):
            self.squares.append(list())

            for col in range(self.width):
                self.squares[row].append(
                    Square(row, col, mines_distribution.pop(0), State.UNTOUCHED)
                )

    def __repr__(self):
        return "<%s.%s object, height=%d, width=%d, mines=%d>" % \
               (self.__class__.__module__, self.__class__.__name__, self.height, self.width, self.mines)

    def __str__(self):

        def format_row(row):
            result = ""

            for square in row:
                if square.state in (State.UNTOUCHED, State.FLAGGED):
                    result += "%s " % square.state.representation
                else:
                    mined_neighbours = [n for n in self.neighbours(square.x, square.y) if n.has_bomb]

                    if len(mined_neighbours) == 0:
                        result += square.state.representation + " "
                    else:
                        result += "%d " % len(mined_neighbours)

            return result

        result = ""

        for row in self.squares:
            result += format_row(row) + "\n"

        return result

    def __iter__(self):
        return iter(self.squares)

    def __contains__(self, key):
        if not (isinstance(key[0], int) and isinstance(key[1], int)):
            raise ValueError("Arguments must be integers (found %s, %s)" % (key[0], key[1]))

        return 0 <= key[0] < len(self.squares) and \
               0 <= key[1] < len(self.squares[key[0]])

    def square(self, x, y):
        return self.squares[x][y]

    def set_state(self, x, y, state):
        self.squares[x][y].state = state

    def neighbours(self, x, y):
        result = list()
        min_row, max_row = max(x - 1, 0), min(x + 1, len(self.squares) - 1)
        min_col, max_col = max(y - 1, 0), min(y + 1, len(self.squares[x]) - 1)

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                if (row, col) != (x, y):
                    result.append(self.squares[row][col])

        return result

    @staticmethod
    def _random_mines_distribution(empty_squares, mined_squares):
        distribution = [False for i in range(empty_squares)]
        distribution.extend([True for i in range(mined_squares)])
        shuffle(distribution)

        return distribution
