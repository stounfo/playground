from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Value
import asyncio
from functools import partial


shared_counter = None


def increment_and_print(to_print):
    with shared_counter.get_lock():
        shared_counter.value += 1
    print(to_print)


def init(counter):
    global shared_counter
    shared_counter = counter


async def main():
    counter = Value("i", 0)
    with ProcessPoolExecutor(initializer=init, initargs=(counter,)) as pool:
        futures = (
            asyncio.get_running_loop().run_in_executor(
                pool, partial(increment_and_print, word)
            )
            for word in ("hello", "how", "are", "you")
        )
        await asyncio.gather(*futures)
        print("shared_counter:", counter.value)


if __name__ == "__main__":
    asyncio.run(main())
