import pytest
import os
import os.path
import json
import pwd
import subprocess
import yt.wrapper as yt

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'datafiles',
)

yt.config.set_proxy('hahn')


class InputTableMockFixture(object):
    def __init__(self, filename):
        super(InputTableMockFixture, self).__init__()
        self.data = json.load(open(filename, 'r'))

    def get(self):
        '''
        Returns iterator over table. Similar to yt.wrapper.read_table
        '''
        return iter(self.data)


@pytest.fixture
def yt_input_table_tracks():
    datafile = os.path.join(FIXTURE_DIR, 'built_tracks_table.json')
    return InputTableMockFixture(datafile)


class FileLoader(object):
    def __init__(self, root):
        self.root = root

    def filepath(self, filename):
        return os.path.join(self.root, filename)


@pytest.fixture
def load():
    return FileLoader(FIXTURE_DIR)


class YtTableUploader(object):
    def __init__(self, load):
        self.load = load
        self.user = pwd.getpwuid(os.getuid()).pw_name
        self.infer_schema_file = load.filepath('restore_schema.yql')

    def create_temp_table(self):
        table_path = yt.create_temp_table('//tmp/{}'.format(self.user),
                                          prefix='graph-metrics-test')
        return table_path

    def upload_yql_table(self, relative_filepath):
        filepath = self.load.filepath(relative_filepath)

        assert os.path.exists(filepath)
        assert len(self.user) > 0

        table_path = self.create_temp_table()

        environment = os.environ.copy()

        with open(os.path.expanduser('~/.yql/token'), 'r') as token_file:
            environment['YQL_TOKEN'] = token_file.read().strip()

        assert subprocess.call(['yql', 'upload_table', '-c', 'hahn',
                                '-t', table_path,
                                '-i', filepath],
                               env=environment) == 0

        # Table is uploaded without yql info. We have to restore it.
        yql_table_path = self.create_temp_table()
        assert subprocess.call(['yql',
                                '-i', self.infer_schema_file,
                                '--parameter-input={}'.format(table_path),
                                '--parameter-output={}'.format(yql_table_path)
                                ]) == 0

        return str(yql_table_path)

    def get_discard_table(self):
        return self.create_temp_table()


@pytest.fixture
def yt_table_loader(load):
    return YtTableUploader(load)
