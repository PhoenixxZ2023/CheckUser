import sys

import checkuser.checker.cli as check_user_cli
import checkuser.service.cli as service_cli
import checkuser.web.cli as web_cli

from checkuser.utils.config import args_handler as config_args_handler
from checkuser.utils import base_cli

if sys.version_info < (3, 6):
    print('Python 3.6 or higher is required.')
    sys.exit(1)


def args_handler(args):
    config_args_handler(args)
    check_user_cli.args_handler(args)
    service_cli.args_handler(args)
    web_cli.args_handler(args)


def main():
    if len(sys.argv) == 1:
        base_cli.print_help()
        return

    args = base_cli.parse_args()
    args_handler(args)


if __name__ == '__main__':
    sys.exit(main())
