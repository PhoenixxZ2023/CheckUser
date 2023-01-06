from ..utils import base_cli
from ..service import ServiceManager

base_cli.add_argument('--create-service', action='store_true', help='Create service')
base_cli.add_argument('--remove-service', action='store_true', help='Remove service')

base_cli.add_argument('--start', action='store_true', help='Start server')
base_cli.add_argument('--stop', action='store_true', help='Stop server')
base_cli.add_argument('--restart', action='store_true', help='Restart server')
base_cli.add_argument('--status', action='store_true', help='Check server status')


def args_handler(args):
    service_manager = ServiceManager()

    if args.create_service:
        service_manager.create_service()

    if args.remove_service:
        service_manager.remove_service()

    if args.start:
        service_manager.start()

    if args.stop:
        service_manager.stop()

    if args.restart:
        service_manager.restart()

    if args.status:
        print(service_manager.status())
