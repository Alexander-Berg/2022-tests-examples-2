import json

import bson
import bson.json_util
import pytest
import yt.yson

from taxi_tests import json_util


class YtHook(json_util.VarHook):
    def __init__(self, variables, yson):
        super(YtHook, self).__init__(variables)
        self.yson = yson

    def __call__(self, obj):
        if self.yson:
            updated_obj = bson.json_util.object_hook(obj)
        else:
            updated_obj = super(YtHook, self).__call__(obj)
        return updated_obj


class YtContext:
    def __init__(self):
        self.select_rows = {}
        self.lookup_rows = {}
        self.read_table = {}
        self.exception_queries = None
        self.exists = set()
        self.paths = set()
        self.created_paths = {}

    def set_exception_queries(self, exception_queries):
        self.exception_queries = exception_queries

    def add_select_rows_response(
            self, query, filename, variables=None, yson=False,
    ):
        if variables is None:
            variables = {}
        self.select_rows[query] = {
            'filename': filename,
            'data': None,
            'variables': variables,
            'yson': yson,
        }

    def add_lookup_rows_response(
            self, data, filename, variables=None, yson=False,
    ):
        if variables is None:
            variables = {}
        self.lookup_rows[data] = {
            'filename': filename,
            'data': None,
            'variables': variables,
            'yson': yson,
        }

    def add_read_table_response(
            self, path, filename=None, data=None, variables=None, yson=False,
    ):
        if variables is None:
            variables = {}
        self.read_table[path] = {
            'filename': filename,
            'data': data,
            'variables': variables,
            'yson': yson,
        }

    def add_exists(self, path):
        self.exists.add(path)

    def add_paths(self, paths):
        for path in paths:
            self.paths.add(path)

    def remove_path(self, path):
        if path in self.paths:
            self.paths.remove(path)
            return True
        return False

    def get_created_paths(self):
        return self.created_paths

    def add_created_path(
            self,
            path: str,
            node_type: str,
            force: bool,
            recursive: bool,
            ignore_existing: bool,
    ):
        self.created_paths[path] = (
            node_type,
            force,
            recursive,
            ignore_existing,
        )


@pytest.fixture(autouse=True)
def yt_proxy(mockserver):
    @mockserver.json_handler('/yt/yt-test/hosts')
    def proxy_response_test(request):
        return [mockserver.url('yt/yt-test')]

    @mockserver.json_handler('/yt/yt-repl/hosts')
    def proxy_response_repl(request):
        return [mockserver.url('yt/yt-repl')]


@pytest.fixture
def yt_client(mockserver, load_binary, load_json):
    context = YtContext()

    def dump_item(data, yson):
        if not yson:
            return json.dumps(data)
        result = {}
        for key, value in data.items():
            # 'doc' field in YT is a raw bson document
            if key == 'doc' or key.endswith('.doc'):
                value = bson.BSON.encode(value)
            elif isinstance(value, str):
                value = value.encode()
            elif not isinstance(value, int) and value is not None:
                raise RuntimeError('Invalid YT value %s' % value)
            result[key.encode()] = value
        return yt.yson.dumps(result, yson_format='binary', encoding=None)

    def load_reply(params):
        yson = params['yson']
        data = (
            load_json(
                params['filename'],
                object_hook=YtHook(params['variables'], yson),
            )
            if params['filename']
            else params['data']
        )

        delimiter = b';' if yson else '\n'
        if isinstance(data, dict):
            reply = dump_item(data, yson)
        elif isinstance(data, list):
            reply = delimiter.join([dump_item(item, yson) for item in data])
        else:
            raise RuntimeError(
                'YT mock data must be an object or array of objects',
            )
        return reply

    def content_type(params):
        if params['yson']:
            return 'application/x-yt-yson-binary'
        return 'application/json'

    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows(request):
        if 'X-YT-Parameters' not in request.headers:
            return {}

        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        if 'query' not in yt_parameters:
            return {}

        query = str(yt_parameters['query'])
        if query not in context.select_rows:
            if context.exception_queries is None:
                return {}
            assert query in context.exception_queries

            return {}

        params = context.select_rows[query]
        return mockserver.make_response(
            load_reply(params), content_type=content_type(params),
        )

    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows(request):
        data = request.data.decode()
        if data not in context.lookup_rows:
            return {}

        params = context.lookup_rows[data]
        return mockserver.make_response(
            load_reply(params), content_type=content_type(params),
        )

    @mockserver.json_handler('/yt/yt-test/api/v3/read_table')
    @mockserver.json_handler('/yt/yt-repl/api/v3/read_table')
    def read_table(request):
        if 'X-YT-Parameters' not in request.headers:
            return mockserver.make_response(status=400)

        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        if 'path' not in yt_parameters:
            return mockserver.make_response(status=400)

        path = str(yt_parameters['path'])
        if path not in context.read_table:
            return mockserver.make_response(status=400)

        params = context.read_table[path]
        return mockserver.make_response(
            load_reply(params), content_type=content_type(params),
        )

    @mockserver.json_handler('/yt/yt-test/api/v3/exists')
    @mockserver.json_handler('/yt/yt-repl/api/v3/exists')
    def exists(request):
        if 'X-YT-Parameters' not in request.headers:
            return mockserver.make_response(status=400)

        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        if 'path' not in yt_parameters:
            return mockserver.make_response(status=400)

        path = str(yt_parameters['path'])

        exists = path in context.exists
        return mockserver.make_response(str(exists).lower())

    @mockserver.json_handler('/yt/yt-test/api/v3/remove')
    @mockserver.json_handler('/yt/yt-repl/api/v3/remove')
    def remove(request):
        if 'X-YT-Parameters' not in request.headers:
            return mockserver.make_response(status=400)

        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        if 'path' not in yt_parameters:
            return mockserver.make_response(status=400)

        path = yt_parameters['path']
        force = yt_parameters.get('force', False)
        if not path:
            return mockserver.make_response(status=400)

        is_path_removed = context.remove_path(path)
        if not is_path_removed and not force:
            return mockserver.make_response(status=400)

        return mockserver.make_response(
            'true', content_type='application/json',
        )

    @mockserver.json_handler('/yt/yt-test/api/v3/create')
    @mockserver.json_handler('/yt/yt-repl/api/v3/create')
    def create(request):
        if 'X-YT-Parameters' not in request.headers:
            return mockserver.make_response(status=400)

        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        if 'path' not in yt_parameters:
            return mockserver.make_response(status=400)

        path = yt_parameters['path']
        if not path:
            return mockserver.make_response(status=400)

        node_type = yt_parameters['type']
        if not node_type:
            return mockserver.make_response(status=400)

        force = yt_parameters.get('force', False)
        ignore_existing = yt_parameters.get('ignore_existing', False)
        recursive = yt_parameters.get('recursive', False)

        context.add_created_path(
            path,
            node_type,
            force=force,
            recursive=recursive,
            ignore_existing=ignore_existing,
        )

        return mockserver.make_response(
            'abacaba', content_type='application/json',
        )

    return context


@pytest.fixture(autouse=True)
def _yt_secondary_requests(mockserver):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-test/api/v3/read_table')
    @mockserver.json_handler('/yt/yt-repl/api/v3/read_table')
    @mockserver.json_handler('/yt/yt-test/api/v3/remove')
    @mockserver.json_handler('/yt/yt-repl/api/v3/remove')
    @mockserver.json_handler('/yt/yt-test/api/v3/exists')
    @mockserver.json_handler('/yt/yt-repl/api/v3/exists')
    @mockserver.json_handler('/yt/yt-test/api/v3/create')
    @mockserver.json_handler('/yt/yt-repl/api/v3/create')
    def yt_request_handler(request):
        return mockserver.make_response(status=500)
