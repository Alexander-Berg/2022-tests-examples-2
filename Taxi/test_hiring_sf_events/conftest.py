# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import collections
import datetime
import functools
import json
import random
import uuid

import pytest

import hiring_sf_events.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_sf_events.generated.service.pytest_plugins']

DOCUMENTS_COUNT = 50


EventRow = collections.namedtuple(
    'Row',
    [
        'id',
        'task_id',
        'lead_id',
        'status',
        'occurred_at',
        'payload',
        'sent_at',
        'ignored',
        'fail_message',
        'fail_occurred_at',
    ],
)


def hex_uuid():
    return uuid.uuid4().hex


def fill_template(template, kwargs):
    json_str = template.format(**kwargs)
    return json.loads(json_str)  # noqa: F405


@pytest.fixture  # noqa: F405
def load_template_and_fill(load):
    def loader(name, kwargs):
        template = load[name]
        return fill_template(template, kwargs)

    return loader


@pytest.fixture  # noqa: F405
def generate_documents(load, load_json):
    names = load_json('personality_source.json')['names']
    template_default = load('document_template_json.txt')
    statuses_default = tuple(STATUSES)

    def _wrapper(template=template_default, statuses=statuses_default):
        def generate_occurred_at():
            occurred_at_dt = datetime.datetime.now() - datetime.timedelta(
                seconds=random.random() * 2,
            )
            return occurred_at_dt

        def generate_info():
            info = {}
            sex = random.choice(('female', 'male'))
            first = random.choice(names[sex]['first_names'])
            second = random.choice(names[sex]['second_names'])
            occurred_at = generate_occurred_at()
            call_result_dt = occurred_at - datetime.timedelta(
                seconds=100 * random.random(),
            )
            info['fullname'] = ' '.join((first, second))
            info['sex'] = sex
            info['lead_id'] = hex_uuid()
            info['task_id'] = hex_uuid()
            info['operator_id'] = hex_uuid()
            info['status'] = random.choice(statuses)
            info['occurred_at'] = occurred_at.isoformat()
            info['call_result_dt'] = call_result_dt.isoformat()
            return info

        while True:
            document = fill_template(template, generate_info())
            yield document

    return _wrapper


@pytest.fixture  # noqa: F405
def post_document(web_app_client):
    async def _wrapper(document: dict, *, status=200) -> dict:
        async with web_app_client.post(
                '/v1/send-event', json=document,
        ) as response:
            assert response.status == status
            response_body = await response.json()
        return response_body

    return _wrapper


STATUSES = ['PREPARED', 'SENT_TO_OKTELL', 'GOT_RESULT']


@pytest.fixture  # noqa: F405
@pytest.mark.config(HIRING_SF_EVENTS_STATUSES=STATUSES)  # noqa: F405
async def fill_initial_data(post_document, generate_documents):
    def update_status(document, statuses):
        new_status = random.choice(list(set(STATUSES) - set(statuses)))
        document['status'] = new_status

    generator = generate_documents()

    i = 0
    while i < DOCUMENTS_COUNT:
        doc = next(generator)
        j = 0
        used_statuses = []
        while (
                i < DOCUMENTS_COUNT
                and j < len(STATUSES)
                and (j == 0 or random.random() > 0.5)
        ):
            update_status(doc, used_statuses)
            res = await post_document(doc)
            assert res['code'] == 'OK'
            used_statuses.append(doc['status'])
            j += 1
            i += 1


@pytest.fixture
def salesforce_auth(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    async def salesforce_auth_handler(request):
        return {
            'access_token': 'asdfsdf',
            'instance_url': 'asdfsdf',
            'id': 'asdfsdaf',
            'token_type': 'asdf',
            'issued_at': 'asdf',
            'signature': 'asdfsdf',
        }

    return salesforce_auth_handler


@pytest.fixture  # noqa: F405
def salesforce(mockserver, salesforce_auth):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        r'/salesforce/services/data/v50.0/sobjects/Task/(?P<task_id>\w+)',
        regex=True,
    )
    async def salesforce_create_task_handler(request, task_id):
        return mockserver.make_response(status=204)


def main_configuration(func):
    @pytest.mark.config(HIRING_SF_EVENTS_STATUSES=STATUSES)  # noqa: F405
    @pytest.mark.usefixtures('salesforce')
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


@pytest.fixture  # noqa: F405
def get_all_events(pgsql, load):
    db = pgsql['hiring_sf_events']
    query = load('all_events.sql')

    def _do_it():
        cursor = db.cursor()
        cursor.execute(query)
        rows = (EventRow(*record) for record in cursor)
        return DBEvents(rows)

    return _do_it


@pytest.fixture
def simple_secdist(simple_secdist):
    # в нужные секции дописываем свои значения
    simple_secdist['settings_override'].update(
        {
            'INFRANAIM_APIKEYS': {'driveryandex': 'token_driveryandex'},
            'SALESFORCE': {
                'client_id': 'test',
                'client_secret': '0000',
                'grant_type': 'test',
                'password': 'test',
                'username': 'test',
            },
        },
    )
    return simple_secdist


class DBEvents:
    def __init__(self, all_rows):
        self.ignored = []
        self.sent = []
        self.not_processed = []
        self.failures = []

        self._filter(all_rows)

    def _filter(self, rows):
        ignored = []
        sent = []
        not_processed = []
        failures = []
        for row in rows:
            if row.ignored:
                ignored.append(row)
                if row.fail_message:
                    failures.append(row)
            elif row.sent_at:
                sent.append(row)
            else:
                not_processed.append(row)
        self.ignored = ignored
        self.sent = sent
        self.not_processed = not_processed
        self.failures = failures

    def __len__(self):
        return len(self.ignored) + len(self.sent) + len(self.not_processed)
