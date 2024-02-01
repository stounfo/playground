from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import partial
import threading

counter = 0
lock = threading.Lock()


def increment_and_print(to_print):
    global counter
    with lock:
        counter += 1
    print(to_print)


async def main():
    with ThreadPoolExecutor() as pool:
        futures = (
            asyncio.get_running_loop().run_in_executor(
                pool, partial(increment_and_print, word)
            )
            for word in ("hello", "how", "are", "you")
        )
        await asyncio.gather(*futures)
        print("counter:", counter)


asyncio.run(main())
