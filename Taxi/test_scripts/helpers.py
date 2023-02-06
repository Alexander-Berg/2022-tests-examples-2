import copy
import datetime
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
    'url': 'fake-url',
    'version': 1,
    'organization': 'taxi',
    'execute_type': 'python',
}


def get_script_doc(doc_update):
    script_doc = copy.deepcopy(SCRIPT_TEMPLATE)
    script_doc['_id'] = uuid.uuid4().hex
    script_doc['request_id'] = uuid.uuid4().hex

    # After _id generation so it can be overriden
    script_doc.update(doc_update)
    if 'created' in doc_update and 'updated' not in doc_update:
        script_doc['updated'] = doc_update['created']
    if 'status' in doc_update:
        if doc_update['status'] in scripts_db.RUNNING_OR_LATER_STATUSES:
            if 'started_running_at' not in script_doc:
                script_doc['started_running_at'] = datetime.datetime.utcnow()

    return script_doc
