from enum import Enum, unique
from random import shuffle, random
from itertools import chain
from threading import RLock


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
    """ Problem 3, point b. Thread safety argument:\n
    This thread safety argument is only a draft, and could potentially contain errors,
    imperfections or lack some considerations.
    Thread safety is currently ensured in Board only. The Square class and any other lack
    any type of coverage.

    Every method where the representation of Board is:
        1. Read;
        2. Changed
    is wrapped, through some Python construct, by a thread safety primitive.\n
    This means that, as long as we rely on our understanding of thread safety
    principles, a method which 1. wishes to read a relevant part of the representation of Board must wait any other
    method which is invoked in another thread and which comprises some observer (or mutator) code, and hence is
    wrapped by a thread safety primitive. (As stated before, it is assumed that every observer or mutator method is
    wrapped by one of these primitives, and so we take this fact for granted, however true or false it may be.
    There's only one creator method (__init__) and that doesn't need protection; there are also some producer methods,
    but they are static and they too don't need any control.) And a mutator method which 2. wants to access some data
    must wait that any observer method finishes reading the data at the state it started, and that any mutator method
    modifies its data in a manner which is consistent with how it started.

    Clearly the paragraph above re-explains some general thread-safety techniques. If we wished to give those for
    granted we could also omit it, and consider only what locking primitives are used where. In that case, it would be
    easy to illustrate that the techniques employed are merely one locking technique (more specifically, locking with
    reentrant locks) and that the application of this to the body (or part of it) of an observer or mutator method is
    enough to ensure thread safety.

    In a less theoretical way, thread safety of this class is ensured by a test included in board_test.py. But I'll
    limit myself to only indicating that there is such a test, and won't explain how it works or how it guarantees
    thread safety on this class.
    """
    # Height, width, mines_count number
    DIFF_EASY = (9, 9, 10)
    DIFF_INTERMEDIATE = (16, 16, 40)
    DIFF_HARD = (16, 30, 99)

    def __init__(self, boolean_grid):
        self.squares = list()
        self.lock: RLock = RLock()

        self.lock.acquire()

        for row in range(len(boolean_grid)):
            self.squares.append(list())

            for col in range(len(boolean_grid[row])):
                self.squares[row].append(
                    Square(row, col, boolean_grid[row][col], State.UNTOUCHED)
                )

        self._check_state()
        self.lock.release()

    @staticmethod
    def create_from_probability(height, width, bomb_probability=0.25):
        """
        Create a new board by supplying a **height**, a **width** and a bomb probability parameters.

        :param height: number of rows of the board, each with an even number of elements.
        :param width: number of elements for each row.
        :param bomb_probability: the probability that a cell of the grid has a bomb during creation.
            **bomb_probability** must belong to [0, 1).
        :return: a new Board instance.
        """
        if height * width <= 0:
            raise ValueError("The grid size must be greater than 0 (found %d)" % height * width)
        if not 0 <= bomb_probability < 1:
            raise ValueError("It must be 0 <= bomb_probability <= 1 (bomb_probability = %f)" % bomb_probability)

        squares = list()

        for square in range(height * width):
            squares.append(random() <= bomb_probability)

        return Board(Board._list_to_grid(squares, height, width))

    @staticmethod
    def create_from_difficulty(difficulty=DIFF_EASY):
        """
        Create a new board by supplying a pre-made or a custom difficulty level.

        :param difficulty: a (**height**, **width**, **mines**) tuple.
        :return: a Board instance with **height** rows, each **width**-elements wide, containing
            **mines** mines randomly interspersed in its grid.
        """
        height, width, mines = difficulty

        if height * width <= 0:
            raise ValueError("The grid size must be greater than 0 (found %d)" % height * width)
        if not 0 < mines < height * width:
            raise ValueError("0 < mines < %d not true (mines = %d)" % (height * width, mines))

        squares = Board._random_mines_distribution((height * width) - mines, mines)

        return Board(Board._list_to_grid(squares, height, width))

    @staticmethod
    def create_from_file(path):
        """
        Create a new board as instructed in Problem 4 of the assignment.

        :param path: a string representing a file containing a well-formatted grid of 0s and 1s.
        :return: a new Board instance.
        """

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
        with self.lock:
            return "<'%s.%s' object, height=%d, width=%d, mines_count=%d>" % \
                   (self.__class__.__module__, self.__class__.__name__, self.height(), self.width(), self.mines_count())

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
        self.lock.acquire()

        for row in self.squares:
            result += format_row(row) + "\n"

        self.lock.release()

        return result

    def __len__(self):
        with self.lock:
            return sum([len(row) for row in self.squares])

    def __contains__(self, key):
        if not (isinstance(key[0], int) and isinstance(key[1], int)):
            raise ValueError("Arguments must be integers (found %s, %s)" % (key[0], key[1]))

        with self.lock:
            return 0 <= key[0] < len(self.squares) and \
                   0 <= key[1] < len(self.squares[key[0]])

    def __iter__(self):
        with self.lock:
            return iter(chain(*self.squares))

    def square(self, row, col):
        with self.lock:
            return self.squares[row][col]

    def height(self):
        with self.lock:
            return len(self.squares)

    def width(self):
        with self.lock:
            return len(self.squares[0]) if len(self.squares) > 0 else 0

    def mines_count(self):
        """
        :return: an int indicating the number of squares where has_bomb evaluates to true, i.e. those squares
            which have a bomb, or are "mined".
        """
        with self.lock:
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
        self.lock.acquire()

        if (row, col) not in self:
            raise ValueError("%d, %d coordinates are out of range" % (row, col))

        self.squares[row][col].state = state

        if state == State.DUG and not self.squares[row][col].has_bomb:
            neighbors = self.neighbors(row, col)
            nearby_bombs = len([n for n in neighbors if n.has_bomb])

            if nearby_bombs == 0:
                for n in [s for s in neighbors if s.state != State.DUG]:
                    self.set_state(n.row, n.col, State.DUG)

        self.lock.release()

    def neighbors(self, row, col):
        """
        :return: a list containing all those squares which are one square away from the (row, col) square, that is its
            "neighbours".
        """
        self.lock.acquire()

        result = list()
        min_row, max_row = max(row - 1, 0), min(row + 1, len(self.squares) - 1)
        min_col, max_col = max(col - 1, 0), min(col + 1, len(self.squares[row]) - 1)

        for x in range(min_row, max_row + 1):
            for y in range(min_col, max_col + 1):
                if (x, y) != (row, col):
                    result.append(self.squares[x][y])

        self.lock.release()

        return result

    def _check_state(self):
        """
        Performs validity checks on the current instance, raising relevant exceptions when detecting an invalid state.
        :return: True if no inconsistencies were found within the current instance.
        """
        self.lock.acquire()
        expected_line_length = len(self.squares[0]) if len(self.squares) > 0 else None

        for line in self.squares:
            types = {type(square) for square in line}

            if {Square} != types:
                raise ValueError("The board can only contain Square variables within its grid")
            if len(line) != expected_line_length:
                raise ValueError("Found a %d-element-wide line, expected %d" % (len(line), expected_line_length))

        self.lock.release()

        return True

    @staticmethod
    def _random_mines_distribution(empty_squares, mined_squares):
        distribution = [False for i in range(empty_squares)]
        distribution.extend([True for i in range(mined_squares)])
        shuffle(distribution)

        return distribution

    @staticmethod
    def _list_to_grid(squares, height, width):
        """
        Utility method used to convert a flat list of boolean values (representing mined squares) to
        a multi-dimensional list with specified height and width.

        :param squares: one-dimensional list of squares.
        :param height: height of the resulting grid.
        :param width: number of elements for each of the **height** rows.
        :return: a grid-like list with the same values as **squares**.
        """
        return [squares[i * width:(i * width) + width] for i in range(height)]

    def toggle_dug(self, toggles=1):
        """
        Switches the state of every square contained in this board between UNTOUCHED and DUG (see the code
        for more info). If the state of a square is FLAGGED no modification occurs.\n
        This method is primarily used for debug purposes.
        """
        self.lock.acquire()

        for i in range(toggles):
            for s in self:
                if s.state == State.UNTOUCHED:
                    # self.set_state(s.row, s.col, State.DUG)
                    s.state = State.DUG
                elif s.state == State.DUG:
                    # self.set_state(s.row, s.col, State.UNTOUCHED)
                    s.state = State.UNTOUCHED

        self.lock.release()
