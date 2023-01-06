import typing as t
import os


class SSHManager:
    def count_connections(self, username: str) -> int:
        command = 'ps -u %s 2>/dev/null' % username
        result = os.popen(command).readlines()
        return len([line for line in result if 'sshd' in line])

    def get_pids(self, username: str) -> t.List[int]:
        command = 'ps -u %s 2>/dev/null' % username
        result = os.popen(command).readlines()
        return [int(line.split()[0]) for line in result if 'sshd' in line]

    def kill_connection(self, username: str) -> None:
        pids = self.get_pids(username)
        for pid in pids:
            os.kill(pid, 9)

    def count_all_connections(self) -> int:
        list_of_users = []

        for line in open('/etc/passwd'):
            split = line.split(':')

            user_id = int(split[2])
            username = split[0]

            if user_id >= 1000 and username != 'root':
                list_of_users.append(username)

        return sum([self.count_connections(username) for username in list_of_users])
