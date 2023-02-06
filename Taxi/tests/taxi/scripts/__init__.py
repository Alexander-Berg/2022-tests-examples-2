import copy
import datetime
import os.path
import uuid

from taxi.scripts import db as scripts_db


SCRIPT_TEMPLATE = {
    'approvals': [],
    'arguments': ['--arg', 'arg'],
    'comment': 'TEST_1',
    'created': datetime.datetime(2018, 11, 15, 17, 45, 39, 15000),
    'created_by': 'vlmazlov',
    'is_reported': False,
    'local_relative_path': 'fake-project/test.py',
    'project': 'fake-project',
    'python_path': 'FAKE_PYTHON_PATH',
    'status': scripts_db.ScriptStatus.APPROVED,
    'ticket': 'TAXIBACKEND-1',
    'updated': datetime.datetime(2018, 11, 21, 12, 9, 53, 147000),
    'url': (
        'https://github.yandex-team.ru/taxi/tools/blob/'
        '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
        'migrations/m4326_debugging_script.py'
    ),
    'version': 1,
    'features': [],
}


def get_script_doc(doc_update):
    script_doc = copy.deepcopy(SCRIPT_TEMPLATE)
    script_doc['_id'] = uuid.uuid4().hex
    script_doc['request_id'] = uuid.uuid4().hex

    # After _id generation so it can be overriden
    script_doc.update(doc_update)

    return script_doc


def get_static_filepath(filename):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return os.path.join(static_dir, filename)
