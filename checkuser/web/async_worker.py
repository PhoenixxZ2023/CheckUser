import asyncio
import socket
import json

from typing import Tuple

from ..utils import logger
from .utils import HttpParser
from .command_handler import CommandHandler


class Worker:
    def __init__(self, concurrency: int = 5) -> None:
        self.concurrency = concurrency
        self.tasks = []

        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()

        self.command_handler = CommandHandler()

    async def _worker(self):
        while True:
            client, addr = await self.queue.get()

            try:
                logger.info('Client %s:%d connected' % addr)
                await self.handle(client)
            except Exception as e:
                logger.error(f'Error: {e}')
            finally:
                logger.info('Client %s:%d disconnected' % addr)
                client.close()

    async def handle(self, item: socket.socket):
        data = await self.loop.sock_recv(item, 1024)

        parser = HttpParser.of(data.decode('utf-8'))
        response = json.dumps(
            HttpParser.build_response(
                status=403,
                headers={'Content-Type': 'Application/json'},
                body='{"error": "Forbidden"}',
            ),
            indent=4
        )

        if not data or not parser.path:
            await self.loop.sock_sendall(item, response.encode())
            return

        split = parser.path.split('/')

        command = split[1]
        content = split[2].split('?')[0] if len(split) > 2 else None

        logger.info(f'Command: {command}')
        logger.info(f'Content: {content}')

        try:
            response = json.dumps(
                self.command_handler.handle(
                    command, content
                ),
                indent=4,
            )
            response = HttpParser.build_response(
                status=200,
                headers={'Content-Type': 'Application/json'},
                body=response,
            )
        except Exception as e:
            response = HttpParser.build_response(
                status=500,
                headers={'Content-Type': 'Application/json'},
                body=json.dumps({'error': str(e)}, indent=4),
            )

        await self.loop.sock_sendall(item, response.encode())

    async def put(self, item: Tuple[socket.socket, Tuple[str, int]]):
        await self.queue.put(item)

    async def start(self):
        for _ in range(self.concurrency):
            task = self.loop.create_task(self._worker())
            self.tasks.append(task)

    def stop(self):
        for task in self.tasks:
            task.cancel()

        self.loop.create_task(self.queue.join())
        self.loop.stop()
