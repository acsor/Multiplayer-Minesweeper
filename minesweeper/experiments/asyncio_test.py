import asyncio
from random import randrange


def multiply(factors):
    result = factors[0] if len(factors) > 0 else None

    for factor in factors[1:]:
        result *= factor

    return result


def run_multiply(factors):
    if factors is not None and len(factors) > 0:
        print("%s(%s) = %d" % (multiply.__name__, str(factors)[1:-1], multiply(factors)))
    else:
        print(factors)


def main():
    eloop = asyncio.get_event_loop()
    eloop.call_soon(run_multiply, [randrange(1, 100) for i in range(5)])

    eloop.stop()
    eloop.run_forever()


if __name__ == "__main__":
    main()
