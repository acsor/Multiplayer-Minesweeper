from enum import Enum, unique
from random import shuffle
from itertools import chain


@unique
class State(Enum):

    UNTOUCHED = "-"
    FLAGGED = "F"
    DUG = " "

    def __init__(self, representation):
        self.representation = representation


class Square:

    REPR_BOMB = "*"

    def __init__(self, row, col, has_bomb, state):
        self.row, self.col = row, col
        self.has_bomb = has_bomb
        self.state = state

    def __repr__(self):
        return "<'%s.%s' object, row=%d, col=%d, has_bomb=%s, state=%s>" % \
               (self.__class__.__module__, self.__class__.__name__, self.row, self.col,
                self.has_bomb, self.state.name)

    def __str__(self):
        if self.state == State.DUG and self.has_bomb:
            return Square.REPR_BOMB
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
        return "<'%s.%s' object, height=%d, width=%d, mines=%d>" % \
               (self.__class__.__module__, self.__class__.__name__, self.height, self.width, self.mines)

    def __str__(self):

        def format_row(row):
            result = ""

            for square in row:
                if square.state in (State.UNTOUCHED, State.FLAGGED):
                    result += "%s " % str(square)
                elif square.state == State.DUG:
                    if square.has_bomb:
                        result += "%s " % str(square)
                    else:
                        nearby_bombs = len([n for n in self.neighbors(square.row, square.col) if n.has_bomb])

                        if nearby_bombs == 0:
                            result += str(square) + " "
                        else:
                            result += "%d " % nearby_bombs

            return result

        result = ""

        for row in self.squares:
            result += format_row(row) + "\n"

        return result

    def __len__(self):
        return sum([len(row) for row in self.squares])

    def __contains__(self, key):
        if not (isinstance(key[0], int) and isinstance(key[1], int)):
            raise ValueError("Arguments must be integers (found %s, %s)" % (key[0], key[1]))

        return 0 <= key[0] < len(self.squares) and \
               0 <= key[1] < len(self.squares[key[0]])

    def __iter__(self):
        return chain(*self.squares)

    def set_state(self, row, col, state):
        """
        Set the state of a square indicated by (row, col) to state.
        If state is DUG and the current square has no bomb, then its adjacent squares
        are all dug if none of them has a bomb.

        :param row: row coordinate
        :param col: col coordinate
        :param state: State value to set the (row, col) square into
        """
        if (row, col) not in self:
            raise ValueError("%d, %d coordinates are out of range" % (row, col))

        self.squares[row][col].state = state

        if state == State.DUG and not self.squares[row][col].has_bomb:
            neighbors = self.neighbors(row, col)
            nearby_bombs = sum([1 for n in neighbors if n.has_bomb])

            if nearby_bombs == 0:
                for n in filter(lambda x: x.state != State.DUG, neighbors):
                    self.set_state(n.row, n.col, State.DUG)

    def neighbors(self, row, col):
        result = list()
        min_row, max_row = max(row - 1, 0), min(row + 1, len(self.squares) - 1)
        min_col, max_col = max(col - 1, 0), min(col + 1, len(self.squares[row]) - 1)

        for x in range(min_row, max_row + 1):
            for y in range(min_col, max_col + 1):
                if (x, y) != (row, col):
                    result.append(self.squares[x][y])

        return result

    @staticmethod
    def _random_mines_distribution(empty_squares, mined_squares):
        distribution = [False for i in range(empty_squares)]
        distribution.extend([True for i in range(mined_squares)])
        shuffle(distribution)

        return distribution
