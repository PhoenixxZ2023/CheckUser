import socket
import resource
import asyncio

from .async_worker import Worker
from ..utils import logger


try:
    resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
except Exception as e:
    from ..utils.logger import logger
    logger.error('Error: {}'.format(e))


class Server:
    def __init__(self, host: str, port: int, workers: int = 10):
        self.host = host
        self.port = port
        self.workers = workers

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.loop = asyncio.get_event_loop()
        self.worker = Worker(workers)

    async def _start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(512)
        self.socket.setblocking(False)

        logger.info(f'Listening on {self.host}:{self.port}')

        while True:
            await asyncio.sleep(0.1)

            client, addr = await self.loop.sock_accept(self.socket)
            client.settimeout(5)

            await self.worker.queue.put((client, addr))

    def start(self):
        try:
            self.loop.create_task(self.worker.start())
            self.loop.create_task(self._start())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        finally:
            logger.info('Closing server')

            self.socket.close()
            self.worker.stop()
