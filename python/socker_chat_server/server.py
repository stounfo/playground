import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from typing import Iterable


class ServerState:
    def __init__(self):
        self._reader_to_writer_mapping: dict[StreamReader, StreamWriter] = {}

    async def add_client(self, reader: StreamReader, writer: StreamWriter):
        self._reader_to_writer_mapping[reader] = writer
        await self._on_connect(writer)
        asyncio.create_task(self._echo(reader))

    async def _on_connect(self, writer: StreamWriter):
        writer.write(
            f"Welcome! {len(self._reader_to_writer_mapping)} user(s) are online!\n".encode()
        )
        await writer.drain()
        await self._send_all("New user connected!\n")

    async def _echo(self, reader: StreamReader):
        try:
            while (data := await reader.readline()) != b"":
                host, port = reader._transport.get_extra_info("socket").getpeername()
                await self._send_all(f"{host}:{port} {data.decode()}", reader)

            self._reader_to_writer_mapping.pop(reader)
            await self._send_all(
                f"Client disconnected. {len(self._reader_to_writer_mapping)} user(s) are online!\n"
            )
        except Exception as e:
            logging.exception("Error reading from client.", exc_info=e)
            self._reader_to_writer_mapping.pop(reader)

    async def _send_all(self, message: str, except_readers=[StreamReader]):
        for reader in self._reader_to_writer_mapping:
            if reader is not except_readers:
                writer = self._reader_to_writer_mapping[reader]
                try:
                    writer.write(message.encode())
                    await writer.drain()
                except ConnectionError as e:
                    logging.exception("Could not write to client.", exc_info=e)
                    for key, value in self._reader_to_writer_mapping.items():
                        if value == writer:
                            self._reader_to_writer_mapping.pop(key)


async def main():
    server_state = ServerState()

    async def client_connected(reader: StreamReader, writer: StreamWriter) -> None:
        await server_state.add_client(reader, writer)

    server = await asyncio.start_server(client_connected, "127.0.0.1", 8000)

    async with server:
        await server.serve_forever()


asyncio.run(main())
