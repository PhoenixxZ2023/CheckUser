import typing as t


class HttpParser:
    def __init__(self) -> None:
        self.method = None
        self.path = None
        self.headers = {}
        self.body = None

    def parse(self, data: str) -> None:
        lines = data.split('\r\n')
        if not lines:
            return

        first_line = lines[0]
        if not first_line:
            return

        parts = first_line.split(' ')
        if len(parts) != 3:
            return

        self.method = parts[0]
        self.path = parts[1]
        self.headers = self._parse_headers(lines[1:])

    def _parse_headers(self, lines: t.List[str]) -> t.Dict[str, str]:
        headers = {}
        for line in lines:
            parts = line.split(': ')
            if len(parts) != 2:
                continue

            headers[parts[0]] = parts[1]
        return headers

    @classmethod
    def of(cls, data: str) -> 'HttpParser':
        parser = cls()
        parser.parse(data)
        return parser

    @staticmethod
    def build_response(status: str, headers: t.Dict[str, str], body: str) -> str:
        response = f'HTTP/1.1 {status}\r\n'

        for key, value in headers.items():
            response += f'{key}: {value}\r\n'

        response += '\r\n'
        response += body
        return response
