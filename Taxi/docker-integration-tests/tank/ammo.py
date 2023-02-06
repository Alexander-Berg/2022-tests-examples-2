AMMO_FILE_NAME_PATTERN = 'generated_{name}_ammo.txt'

DEFAULT_HEADERS = {
    'Connection': 'close',
    'User-Agent':
        'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)',
    'Accept-Language': 'en-US, en;q=0.8,ru;q=0.6'
}

DEFAULT_TOKEN = 'test_token'


class AmmoBuilder(object):
    def __init__(self, name):
        self.name = name
        self.lines = []

    def add_line(self, line, *args, **kwargs):
        if args or kwargs:
            line = line.format(*args, **kwargs)
        self.lines.append(line)

    def add_query_line(self, method, path):
        self.add_line('{} {} HTTP/1.0', method, path)

    def add_header(self, k, v):
        self.add_line('{}: {}', k, v)

    def add_body(self, body):
        self.add_header('Content-Length', len(body))
        self.add_line('')
        self.add_line(body)

    @property
    def ammo(self):
        ammo = '\n'.join(self.lines) + '\n'
        total_length = len(ammo)
        first_line = '%d %s' % (total_length, self.name)
        ammo = first_line + '\n' + ammo
        return ammo


def make_ammo(name, method, path, headers, body=None):
    ammo_builder = AmmoBuilder(name)
    ammo_builder.add_query_line(method, path)
    for k, v in headers.iteritems():
        ammo_builder.add_header(k, v)
    if body is not None:
        ammo_builder.add_body(body)
    return ammo_builder.ammo


def store_ammo(file_name_pattern, name, ammo_generator):
    file_name = file_name_pattern.format(name=name)
    print 'Making ammo', name
    ammo = ammo_generator()
    with open(file_name, 'w') as f:
        f.write(ammo)
