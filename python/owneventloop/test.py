import socket

import functools
import selectors


class CustomFuture:
    def __init__(self):
        print("CREATING A NEW FUTURE <=====================")
        self._result = None
        self._is_finished = False
        self._done_callback = None

    def result(self):
        return self._result

    def is_finished(self):
        return self._is_finished

    def set_result(self, result):
        self._result = result
        self._is_finished = True
        if self._done_callback:
            self._done_callback(result)

    def add_done_callback(self, fn):
        self._done_callback = fn

    def __await__(self):
        if not self._is_finished:
            yield self
        return self.result()


class CustomTask(CustomFuture):
    def __init__(self, coro, loop):
        print("CREATING A NEW TASK <=====================")
        super(CustomTask, self).__init__()
        self._coro = coro
        self._loop = loop
        self._current_result = None
        self._task_state = None
        loop.register_task(self)

    def step(self):
        try:
            if self._task_state is None:
                self._task_state = self._coro.send(None)
            if isinstance(self._task_state, CustomFuture):
                self._task_state.add_done_callback(self._future_done)
        except StopIteration as si:
            self.set_result(si.value)

    def _future_done(self, result):
        self._current_result = result
        try:
            self._task_state = self._coro.send(self._current_result)
        except StopIteration as si:
            self.set_result(si.value)


class EventLoop:
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self._tasks_to_run = []
        self.current_result = None

    def _register_socket_to_read(self, sock, callback):
        future = CustomFuture()
        try:
            self.selector.get_key(sock)
        except KeyError:
            sock.setblocking(False)
            self.selector.register(
                sock, selectors.EVENT_READ, functools.partial(callback, future)
            )
        else:
            self.selector.modify(
                sock, selectors.EVENT_READ, functools.partial(callback, future)
            )
        return future

    def _set_current_result(self, result):
        self.current_result = result

    async def sock_recv(self, sock):
        print("Registering socket to listen for data...")
        return await self._register_socket_to_read(sock, self.recieved_data)

    async def sock_accept(self, sock):
        print("Registering socket to accept connections...")
        return await self._register_socket_to_read(sock, self.accept_connection)

    def sock_close(self, sock):
        self.selector.unregister(sock)
        sock.close()

    def register_task(self, task):
        self._tasks_to_run.append(task)

    def recieved_data(self, future, sock):
        data = sock.recv(1024)
        future.set_result(data)

    def accept_connection(self, future, sock):
        result = sock.accept()
        future.set_result(result)

    def run(self, coro):
        try:
            self.current_result = coro.send(None)
        except StopIteration as si:
            return si.value

        while True:
            try:
                if isinstance(self.current_result, CustomFuture):
                    self.current_result.add_done_callback(self._set_current_result)
                    if self.current_result.result() is not None:
                        self.current_result = coro.send(self.current_result.result())
                else:
                    self.current_result = coro.send(self.current_result)
            except StopIteration as si:
                return si.value

            for task in self._tasks_to_run:
                task.step()

            self._tasks_to_run = [
                task for task in self._tasks_to_run if not task.is_finished()
            ]

            events = self.selector.select()
            print("Selector has an event, processing...")
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)


async def read_from_client(conn, loop: EventLoop):
    print(f"Reading data from client {conn}")
    try:
        while data := await loop.sock_recv(conn):
            print(f"Got {data} from client!")
    finally:
        loop.sock_close(conn)


async def listen_for_connections(sock, loop: EventLoop):
    while True:
        print("Waiting for connection...")
        conn, _ = await loop.sock_accept(sock)
        CustomTask(read_from_client(conn, loop), loop)
        print(f"I got a new connection from {sock}!")


async def main(loop: EventLoop):
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(("localhost", 8000))
    server_socket.listen()
    server_socket.setblocking(False)

    await listen_for_connections(server_socket, loop)


if __name__ == "__main__":
    event_loop = EventLoop()
    event_loop.run(main(event_loop))
