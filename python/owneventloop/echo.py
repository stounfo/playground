# Very simple echo server using own event loop, event loop is not universal
from functools import partial
import socket
import selectors
from typing import Any


class Future:
    def __init__(self):
        self._done = False
        self._result = None
        self._done_callback = None

    def done(self):
        return self._done

    def result(self):
        return self._result

    def set_result(self, result):
        self._result = result
        self._done = True
        if self._done_callback is not None:
            self._done_callback(result)

    def add_done_callback(self, callback):
        self._done_callback = callback

    def __await__(self):
        if self._done is False:
            yield self
        return self.result()


class Task(Future):
    def __init__(self, coro, loop):
        super(Task, self).__init__()
        self._coro = coro
        self._loop = loop
        self._task_state = None
        loop.register_task(self)

    def step(self):
        try:
            if self._task_state is None:
                self._task_state = self._coro.send(None)
            if isinstance(self._task_state, Future):  # C
                self._task_state.add_done_callback(self._future_done)
        except StopIteration as si:
            self.set_result(si.value)

    def _future_done(self, _):
        try:
            self._task_state = self._coro.send(None)
        except StopIteration as si:
            self.set_result(si.value)


class EventLoop:
    def __init__(self, selector) -> None:
        self._tasks = []
        self._selector = selector

    async def _register_socket(self, socket, event, callback):
        future = Future()
        callback = partial(callback, future)
        try:
            self._selector.register(
                socket,
                event,
                data=callback,
            )
        except KeyError:
            self._selector.modify(
                socket,
                event,
                data=callback,
            )
        return await future

    def _accepted_callback(self, future, client_socket):
        result = client_socket.accept()
        future.set_result(result)

    async def socket_accept(self, server_socket) -> Any:
        return await self._register_socket(
            server_socket, selectors.EVENT_READ, self._accepted_callback
        )

    def _recv_callback(self, future, client_socket):
        data = client_socket.recv(1000)
        future.set_result(data)

    async def socket_recv(self, conn):
        return await self._register_socket(
            conn, selectors.EVENT_READ, self._recv_callback
        )

    def _send_callback(self, future, client_socket, text):
        result = client_socket.send(text)
        future.set_result(result)

    async def socket_send(self, conn, text):
        return await self._register_socket(
            conn, selectors.EVENT_WRITE, partial(self._send_callback, text=text)
        )

    def register_task(self, task):
        self._tasks.append(task)

    def sock_close(self, sock):
        self._selector.unregister(sock)
        sock.close()

    def _set_current_result_callback(self, result):
        self._current_result = result

    def run(self, coro):
        self._current_result = coro.send(None)

        while True:
            if isinstance(self._current_result, Future):
                self._current_result.add_done_callback(
                    self._set_current_result_callback
                )
            else:
                try:
                    self._current_result = coro.send(None)
                except StopIteration as e:
                    return e.value

            for task in self._tasks:
                task.step()

            self._tasks = [task for task in self._tasks if task.done() is not True]

            events = selector.select()

            for key, _ in events:
                key.data(key.fileobj)


async def read_from_client(conn, loop):  # A
    try:
        while data := await loop.socket_recv(conn):
            print(f"Got {data} from client!")
            await loop.socket_send(conn, data)
    finally:
        loop.sock_close(conn)


async def main(server_socket, loop):
    while True:
        conn, _ = await loop.socket_accept(server_socket)
        Task(read_from_client(conn, loop), loop)


server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", 8000))
server_socket.listen()
server_socket.setblocking(False)

selector = selectors.DefaultSelector()

loop = EventLoop(selector)
loop.run(main(server_socket, loop))
