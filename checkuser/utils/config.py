import typing as t
import os
import json

from ..utils import logger, base_cli


class Config:
    CONFIG_FILE = 'config.json'
    PATH_CONFIG = '/etc/checker/'
    PATH_CONFIG_OPTIONAL = os.path.join(os.path.expanduser('~'), 'checker')

    @property
    def path_config(self) -> str:
        path = os.path.join(self.PATH_CONFIG, self.CONFIG_FILE)

        try:
            if not os.path.exists(path):
                os.makedirs(self.PATH_CONFIG, exist_ok=True)
        except PermissionError:
            path = os.path.join(self.PATH_CONFIG_OPTIONAL, self.CONFIG_FILE)

            if not os.path.exists(path):
                os.makedirs(self.PATH_CONFIG_OPTIONAL, exist_ok=True)

        return path

    @property
    def exclude(self) -> t.List[str]:
        return self.config.get('exclude', [])

    @exclude.setter
    def exclude(self, value: t.List[str]):
        if isinstance(value, str):
            value = [value]

        config = self.config
        config['exclude'] = value

        self.save_config(config)

    def include(self, name: str) -> bool:
        config = self.config
        exclude = config.get('exclude', [])

        if name in exclude:
            exclude.remove(name)
            self.save_config(config)
            return True

        return False

    @property
    def port(self) -> int:
        return self.config.get('port', 5000)

    @port.setter
    def port(self, value: int):
        config = self.config
        config['port'] = value
        self.save_config(config)

    @property
    def config(self) -> dict:
        default_config = {
            'exclude': [],
            'port': 5000,
        }

        if os.path.exists(self.path_config):
            with open(self.path_config, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else default_config

        return default_config

    def save_config(self, config: dict = None) -> bool:
        config = config or self.config

        with open(self.path_config, 'w') as f:
            f.write(json.dumps(config, indent=4))

    @staticmethod
    def remove_config() -> None:
        if os.path.exists(Config.PATH_CONFIG):
            os.system('rm -rf %s' % Config.PATH_CONFIG)


base_cli.add_argument('--config', action='store_true', help='Show config')
base_cli.add_argument('--include', nargs='+', help='Campo a ser exibido')
base_cli.add_argument('--exclude', nargs='+', help='Campo a ser exculdo')
base_cli.add_argument('--config-port', type=int, help='Porta')


def args_handler(args):
    if args.config:
        logger.info(Config().config)
        exit(0)

    if args.include:
        for name in args.include:
            Config().include(name)

    if args.exclude:
        for name in args.exclude:
            Config().exclude = name

    if args.config_port:
        Config().port = args.config_port
