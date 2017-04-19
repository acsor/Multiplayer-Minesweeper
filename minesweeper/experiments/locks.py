import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


class Counter:

    SLEEP_TIME = 0.025

    def __init__(self, start_count=0):
        self.count = start_count

    def __str__(self):
        return str(self.count)

    def increment(self, times=1):
        for i in range(times):
            self.count += 1

    def decrement(self, times=1):
        for i in range(times):
            self.count -= 1


class StringStretcher:
    """
    A StringStretcher object lengthens a string s by an increment i by a specified number of times n.
    It can also shorten the string s.

    **Note**: This class does not currently work as intended (it seems impossible to cause race
    conditions).
    """
    SLEEP_TIME = 0.025

    def __init__(self, string, increment):
        self.string: str = string
        self.increment: str = increment

    def __str__(self):
        return str(self.string)

    def __len__(self):
        return len(self.string)

    def add(self, times=1):
        for i in range(times):
            time.sleep(self.SLEEP_TIME)
            # noinspection PyAugmentAssignment
            self.string = self.string + self.increment

    def subtract(self, times=1):
        for i in range(min(len(self.string), times)):
            time.sleep(self.SLEEP_TIME)
            self.string = self.string[:-1]


def main():
    configs = {
        "workers": 11,
        "cycles": 10,
    }
    c = Counter()
    executor = ThreadPoolExecutor(configs["workers"])
    futures = list()

    for i in range(configs["workers"]):
        futures.append(
            executor.submit(
                c.increment if i < configs["workers"] // 2 else c.decrement,
                configs["cycles"]
            )
        )

    wait(futures, None, ALL_COMPLETED)

    print(c)


if __name__ == "__main__":
    main()
