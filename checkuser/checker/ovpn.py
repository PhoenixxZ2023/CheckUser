import os
import socket


class OpenVPNManager:
    def __init__(self, port: int = 7505):
        self.port = port
        self.config_path = '/etc/openvpn/'
        self.config_file = 'server.conf'
        self.log_file = 'openvpn.log'
        self.log_path = '/var/log/openvpn/'

        self.start_manager()

    @staticmethod
    def openvpn_is_running() -> bool:
        status = OpenVPNManager.openvpn_is_installed()

        if status:
            data = os.popen('service openvpn status').read().strip()
            status = data.find('Active: active') > -1

        return status

    @staticmethod
    def openvpn_is_installed() -> bool:
        return os.path.exists('/etc/openvpn/') and os.path.exists('/etc/openvpn/server.conf')

    @property
    def config(self) -> str:
        return os.path.join(self.config_path, self.config_file)

    @property
    def log(self) -> str:
        path = os.path.join(self.log_path, self.log_file)
        if os.path.exists(path):
            return path

        self.log_path = 'openvpn-status.log'
        return os.path.join(self.config_path, self.log_file)

    def create_connection(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', self.port))
        return sock

    def start_manager(self) -> None:
        if os.path.exists(self.config):
            with open(self.config, 'r') as f:
                data = f.readlines()

                management = 'management localhost %d\n' % self.port
                if management in data:
                    return

                data.insert(1, management)

            with open(self.config, 'w') as f:
                f.writelines(data)

            os.system('service openvpn restart')

    def count_connection_from_manager(self, username: str) -> int:
        try:
            soc = self.create_connection()
            soc.send(b'status\n')

            data = b''
            buf = data

            while b'\r\nEND\r\n' not in buf:
                buf = soc.recv(1024)
                data += buf

            soc.close()
            count = data.count(username.encode())
            return count // 2 if count > 0 else 0
        except Exception:
            return -1

    def count_connection_from_log(self, username: str) -> int:
        if os.path.exists(self.log):
            with open(self.log, 'r') as f:
                data = f.read()
                count = data.count(username)

                return count // 2 if count > 0 else 0

        return 0

    def count_connections(self, username: str) -> int:
        count = self.count_connection_from_manager(username)
        return count if count > -1 else self.count_connection_from_log(username)

    def kill_connection(self, username: str) -> None:
        try:
            soc = self.create_connection()
            soc.send(b'kill %s\n' % username.encode())
            soc.close()
        except Exception:
            pass

    def count_all_connections(self) -> int:
        list_of_users = []

        for line in open('/etc/passwd'):
            split = line.split(':')

            user_id = int(split[2])
            username = split[0]

            if user_id >= 1000 and username != 'root':
                list_of_users.append(username)

        return sum([self.count_connections(username) for username in list_of_users])
