from ..utils import base_cli, logger, Config
from ..web import Server

base_cli.add_argument(
    '--start-server',
    action='store_true',
    help='Start server',
)

base_cli.add_argument(
    '--server-host',
    default='0.0.0.0',
    help='Server host',
)

base_cli.add_argument(
    '--server-port',
    type=int,
    help='Server port',
)

base_cli.add_argument(
    '--server-num-workers',
    default=5,
    type=int,
    help='Server number of workers',
)

base_cli.add_argument(
    '--daemon',
    action='store_true',
    help='Daemonize',
)


def args_handler(args):
    if args.start_server:
        if args.server_port is None:
            args.server_port = Config().port

        if args.daemon:
            try:
                __import__('daemon').DaemonContext().open()
            except ImportError:
                logger.warning('Missing library: pip3 install python-daemon')

        server = Server(
            args.server_host,
            args.server_port,
            args.server_num_workers
        )
        server.start()
