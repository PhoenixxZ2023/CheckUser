import os
import sys

from checkuser.utils import logger


class ServiceManager:
    CONFIG_SYSTEMD_PATH = '/etc/systemd/system/'
    CONFIG_SYSTEMD = 'check_user.service'

    @property
    def config(self) -> str:
        return os.path.join(self.CONFIG_SYSTEMD_PATH, self.CONFIG_SYSTEMD)

    @property
    def is_created(self) -> bool:
        is_created = os.path.exists(self.config)

        if not is_created:
            logger.error('Service not created, please run `%s --create-service`', sys.argv[0])

        return is_created

    @property
    def is_enabled(self) -> bool:
        return os.system('systemctl is-enabled %s >/dev/null' % self.CONFIG_SYSTEMD) == 0

    def status(self) -> str:
        if not self.is_created:
            return False

        command = 'systemctl status %s' % self.CONFIG_SYSTEMD
        result = os.popen(command).readlines()
        return ''.join(result)

    def start(self) -> bool:
        if not self.is_created:
            return False

        status = self.status()
        if 'Active: active' not in status:
            os.system('systemctl start %s' % self.CONFIG_SYSTEMD)
            return True

        return False

    def stop(self):
        if not self.is_created:
            return False

        status = self.status()
        if 'Active: inactive' not in status:
            os.system('systemctl stop %s' % self.CONFIG_SYSTEMD)
            return True

        return False

    def restart(self) -> bool:
        if not self.is_created:
            return False

        command = 'systemctl restart %s' % self.CONFIG_SYSTEMD
        return os.system(command) == 0

    def remove_service(self):
        os.system('systemctl stop %s' % self.CONFIG_SYSTEMD)
        os.system('systemctl disable %s' % self.CONFIG_SYSTEMD)
        os.system('rm %s' % self.config)
        os.system('systemctl daemon-reload')

    def create_systemd_config(self) -> bool:
        logger.info('Creating systemd config...')
        config_template = ''.join(
            [
                '[Unit]\n',
                'Description=CheckUser service\n',
                'After=network.target nss-lookup.target\n\n',
                '[Service]\n',
                'Type=simple\n',
                'CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE\n',
                'AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE\n',
                'NoNewPrivileges=true\n',
                'ExecStart=%s --start-server\n' % sys.argv[0],
                'Restart=on-failure\n',
                'User=root\n',
                'Group=root\n\n',
                '[Install]\n',
                'WantedBy=multi-user.target\n',
            ]
        )

        config_path = os.path.join(self.CONFIG_SYSTEMD_PATH, self.CONFIG_SYSTEMD)
        if not os.path.exists(config_path):
            try:
                with open(config_path, 'w') as f:
                    f.write(config_template)

                os.system('systemctl daemon-reload >/dev/null')
                logger.info('Systemd config created.')
            except PermissionError:
                logger.error('Permission denied')

        return self.is_created

    def enable_auto_start(self) -> bool:
        if not self.is_enabled:
            os.system('systemctl enable %s >/dev/null' % self.CONFIG_SYSTEMD)

        return self.is_enabled

    def disable_auto_start(self) -> bool:
        if self.is_enabled:
            os.system('systemctl disable %s >/dev/null' % self.CONFIG_SYSTEMD)

        return not self.is_enabled

    def create_service(self) -> bool:
        if self.create_systemd_config():
            self.enable_auto_start()

            return True

        return False
