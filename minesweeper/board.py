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
    # Height, width, mines_count number
    DIFF_EASY = (9, 9, 10)
    DIFF_INTERMEDIATE = (16, 16, 40)
    DIFF_HARD = (16, 30, 99)

    def __init__(self, boolean_grid):
        self.squares = list()

        for row in range(len(boolean_grid)):
            self.squares.append(list())

            for col in range(len(boolean_grid[row])):
                self.squares[row].append(
                    Square(row, col, boolean_grid[row][col], State.UNTOUCHED)
                )

        self._check_state()

    @staticmethod
    def from_difficulty(difficulty=DIFF_EASY):

        height, width, mines = difficulty
        mines_distribution = Board._random_mines_distribution((height * width) - mines, mines)
        # The line of code below turns mines_distribution from a flat list of boolean values to a multi-dimensional
        # list containing the same values.
        grid = [mines_distribution[i * width:(i * width) + width] for i in range(height)]

        return Board(grid)

    @staticmethod
    def from_file(path):

        def read_line(text_line):
            sep = " "
            encoding = {'0': False, '1': True}

            # dict.get() returns None when a given argument is not contained within the dict keys
            line = [encoding.get(i) for i in text_line.strip().split(sep)]

            if None in line:
                raise ValueError("Found invalid content in '%s'. Every line can contain only 0s and 1s" % path)

            return line

        with open(path) as f:
            lines = [read_line(line) for line in f]

            for line in lines:
                if len(line) != len(lines):
                    raise ValueError("Found %d wide line in a %d tall grid, square grid expected" %
                                     (len(line), len(lines)))

        return Board(lines)

    def __repr__(self):
        return "<'%s.%s' object, height=%d, width=%d, mines_count=%d>" % \
               (self.__class__.__module__, self.__class__.__name__, len(self.squares), self.width(), self.mines_count())

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

    def height(self):
        return len(self.squares)

    def width(self):
        return len(self.squares[0]) if len(self.squares) > 0 else 0

    def mines_count(self):
        return len([square for square in self if square.has_bomb])

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
            nearby_bombs = len([n for n in neighbors if n.has_bomb])

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

    def _check_state(self):
        """
        Performs validity checks on the current instance, raising relevant exceptions when detecting an invalid state.
        :return: True if no inconsistencies were found within the current instance.
        """
        expected_line_length = len(self.squares[0]) if len(self.squares) > 0 else None

        for line in self.squares:
            types = {type(square) for square in line}

            if {Square} != types:
                raise ValueError("The board can only contain Square variables within its grid")
            if len(line) != expected_line_length:
                raise ValueError("Found a %d-element-wide line, expected %d" % (len(line), expected_line_length))

        return True

    @staticmethod
    def _random_mines_distribution(empty_squares, mined_squares):
        distribution = [False for i in range(empty_squares)]
        distribution.extend([True for i in range(mined_squares)])
        shuffle(distribution)

        return distribution
