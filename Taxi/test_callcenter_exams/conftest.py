# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import functools
import json
import typing

import pytest

import callcenter_exams.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['callcenter_exams.generated.service.pytest_plugins']


SETTINGS_OVERRIDE = {
    'CALLCENTER_EXAMS_MDS_S3_AUDIOLINKS': {
        'url': 's3.mds.yandex.net',
        'bucket': 'audiolinks',
        'access_key_id': 'key_to_access',
        'secret_key': 'very_secret',
    },
}


@pytest.fixture
def mock_sticker_send(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/sticker/send/')
        def handle_urls(request, *args, **kwargs):
            return {}

    return Context()


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(SETTINGS_OVERRIDE)
    return simple_secdist


@pytest.fixture
def personal(mockserver, response_mock, load_json):
    @mockserver.json_handler('/personal/v1/emails/find')
    def _personal_emails(request):
        return {'id': 'user_id', 'value': 'user_email'}


def main_configuration(func):
    @pytest.mark.config(
        TVM_RULES=[{'dst': 'personal', 'src': 'callcenter-exams'}],
    )
    @pytest.mark.usefixtures('personal')
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


@pytest.fixture
def mock_startrack(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        'http://test-startrack-url/issues/EXAM-123/comments', 'POST',
    )
    def comment(*args, **kwargs):
        return response_mock(
            text=json.dumps(
                {
                    'expand': 'string',
                    'self': 'http://example.com',
                    'id': 0,
                    'longId': '0123456789abcdef01234567',
                    'createdBy': {
                        'self': 'http://example.com',
                        'id': 'string',
                        'version': 0,
                        'key': 'string',
                        'display': 'string',
                    },
                    'updatedBy': {
                        'self': 'http://example.com',
                        'id': 'string',
                        'version': 0,
                        'key': 'string',
                        'display': 'string',
                    },
                    'createdAt': '2021-05-16T05:05:57.253Z',
                    'updatedAt': '2021-05-16T05:05:57.542Z',
                    'reactionsCount': {'property1': 0, 'property2': 0},
                    'usersReacted': {'property1': [], 'property2': []},
                    'version': 0,
                },
            ),
            status=201,
        )

    return comment


@pytest.fixture
def mock_startrack_update_ticket(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        'http://test-startrack-url/issues/EXAM-123', 'PATCH',
    )
    def update(*args, **kwargs):
        assert 'examTheory' in kwargs['json']
        return response_mock(text=json.dumps({}), status=200)

    return update


@pytest.fixture
def mock_kiosk(mockserver):
    class MockKiosk:
        @staticmethod
        @mockserver.json_handler('/kiosk/api/v1/programs.json')
        def programs(request):
            assert request.query['external_id'] == 'EXAM-123'
            assert request.headers['KIOSK-API-KEY'] == 'kiosk_api_key'
            return {
                'programs': [
                    {
                        'uuid': 'd985c6b4-136a-413a-8f5a-d0d0fd22e48f',
                        'name': 'Test',
                        'url': (
                            'https://instructor-dev.vmb.co/?programUuid='
                            'd985c6b4-136a413a-8f5a-d0d0fd22e48f&externalId=EXAM-123'  # noqa: E501
                        ),
                        'started': True,
                        'completed': False,
                        'sessions': [
                            {'uuid': 'b3a2427d-ce78-4bd4-b62e-1b1500b14cc5'},
                            {'uuid': '774dd8d4-3196-4384-9ad2-f5726b0e3ab4'},
                            {'uuid': 'c9007db2-174a-4896-92f7-9fc521dc95de'},
                        ],
                    },
                    {
                        'uuid': '5e5cbec6-5ad3-415a-9839-20996de7ddd3',
                        'name': 'Other Test',
                        'url': (
                            'https://instructor-dev.vmb.co/?programUuid='
                            '5e5cbec6-5ad3-415a-9839-20996de7ddd3&externalId=EXAM-123'  # noqa: E501
                        ),
                        'started': True,
                        'completed': True,
                        'sessions': [
                            {'uuid': 'ec5b2c7b-a57f-4765-a633-f12939ed7a1a'},
                        ],
                    },
                ],
            }

        @staticmethod
        @mockserver.json_handler(
            '/kiosk/api/v1/sessions/ec5b2c7b-a57f-4765-a633-f12939ed7a1a',
        )
        def sessions_uuid1(request):
            assert request.headers['KIOSK-API-KEY'] == 'kiosk_api_key'
            return {
                'session': {
                    'uuid': 'ec5b2c7b-a57f-4765-a633-f12939ed7a1a',
                    'organization_name': '',
                    'state': 'completed',
                    'passed': True,
                    'phone': '79999999999',
                    'telegram': '',
                    'email': 'test@example.ru',
                    'grade': '',
                    'reg_info': {
                        'fio': {
                            'name': 'fio',
                            'type': 'fio',
                            'label': '',
                            'value': 'test test test',
                            'string_value': 'test test test',
                        },
                        'email': {
                            'name': 'email',
                            'type': 'email',
                            'label': 'Email',
                            'value': 'test@example.ru',
                            'string_value': 'test@example.ru',
                        },
                        'phone': {
                            'name': 'phone',
                            'type': 'phone',
                            'label': '',
                            'value': '79999999999',
                            'string_value': '79999999999',
                        },
                    },
                    'submitted_forms': [
                        {
                            'form_id': 10,
                            'answers': [
                                {
                                    'label': ' ?',
                                    'text': '',
                                    'meta': {
                                        'raw_value': '',
                                        'control_type': 'longText',
                                    },
                                },
                                {
                                    'label': ' ?',
                                    'text': (
                                        'https://kiosk-dev.vmb.co/private_read/forms/staging/1/'  # noqa: E501
                                        '56db2990-01fa-43da-9da4-06b13c272d15/qvV-0yZODfJVhzaCSFU7Aw.mp4'  # noqa: E501
                                    ),
                                    'meta': {
                                        'raw_value': [
                                            {
                                                'url': (
                                                    'https://kiosk-dev.vmb.co/private_read/forms/staging/'  # noqa: E501
                                                    '1/56db2990-01fa-43da-9da4-06b13c272d15/'  # noqa: E501
                                                    'qvV-0yZODfJVhzaCSFU7Aw.mp4'  # noqa: E501
                                                ),
                                                'size': 524740,
                                                'content_type': 'video/mp4',
                                                'original_filename': '.mp4',
                                            },
                                        ],
                                        'control_type': 'files',
                                    },
                                },
                                {
                                    'label': ' ?',
                                    'text': '',
                                    'meta': {
                                        'raw_value': '',
                                        'control_type': 'longText',
                                    },
                                },
                                {
                                    'label': ' ',
                                    'text': (
                                        'https://kiosk-dev.vmb.co/private_read/forms/staging/1/'  # noqa: E501
                                        '56db2990-01fa-43da-9da4-06b13c272d15/6-nq2iDTANC5P2QHqdznrQ.jpg'  # noqa: E501
                                    ),
                                    'meta': {
                                        'raw_value': [
                                            {
                                                'url': (
                                                    'https://kiosk-dev.vmb.co/private_read/forms/staging/1/'  # noqa: E501
                                                    '56db2990-01fa-43da-9da4-06b13c272d15/'  # noqa: E501
                                                    '6-nq2iDTANC5P2QHqdznrQ.jpg'  # noqa: E501
                                                ),
                                                'size': 130221,
                                                'content_type': 'image/jpeg',
                                                'original_filename': (
                                                    '87494-1-1508804254.jpg'
                                                ),
                                            },
                                        ],
                                        'control_type': 'files',
                                    },
                                },
                            ],
                        },
                    ],
                    'program': {
                        'uuid': '9e0e1163-0950-4d12-933c-665e21220a3c',
                        'name': '1',
                    },
                    'session_exams': [
                        {
                            'exam_state': 'finished',
                            'score': 2,
                            'min_score': 1,
                            'max_score': 2,
                            'grade_by': 'total_sections',
                            'answers': [
                                {
                                    'question': {
                                        'id': 73,
                                        'name': '1 + 1 + 2 + 3 = ?',
                                    },
                                    'answer_options': [
                                        {
                                            'id': 209,
                                            'name': '7',
                                            'correct': True,
                                        },
                                    ],
                                },
                                {
                                    'question': {
                                        'id': 74,
                                        'name': '5 + 4 + 1 = ?',
                                    },
                                    'answer_options': [
                                        {
                                            'id': 212,
                                            'name': '10',
                                            'correct': True,
                                        },
                                    ],
                                },
                                {
                                    'question': {
                                        'id': 73,
                                        'name': '1 + 1 + 2 + 3 = ?',
                                    },
                                    'answer_options': [
                                        {
                                            'id': 209,
                                            'name': '7',
                                            'correct': True,
                                        },
                                    ],
                                },
                            ],
                            'section_results': [
                                {
                                    'section_id': 88,
                                    'section_name': '1',
                                    'grade': '',
                                    'blocking': False,
                                    'score': 1,
                                    'max_score': 1,
                                    'min_score': 1,
                                    'passed': True,
                                },
                                {
                                    'section_id': 89,
                                    'section_name': '2',
                                    'grade': '',
                                    'blocking': False,
                                    'score': 2,
                                    'max_score': 2,
                                    'min_score': 1,
                                    'passed': True,
                                },
                            ],
                        },
                    ],
                },
            }

        @staticmethod
        @mockserver.json_handler(
            '/kiosk/api/v1/sessions/774dd8d4-3196-4384-9ad2-f5726b0e3ab4',
        )
        def sessions_uuid2(request):
            assert request.headers['KIOSK-API-KEY'] == 'kiosk_api_key'
            return {
                'session': {
                    'uuid': 'ec5b2c7b-a57f-4765-a633-f12939ed7a1a',
                    'organization_name': '',
                    'state': 'completed',
                    'passed': True,
                    'phone': '79999999999',
                    'telegram': '',
                    'email': 'test@example.ru',
                    'grade': '',
                    'reg_info': {
                        'fio': {
                            'name': 'fio',
                            'type': 'fio',
                            'label': '',
                            'value': 'test test test',
                            'string_value': 'test test test',
                        },
                        'email': {
                            'name': 'email',
                            'type': 'email',
                            'label': 'Email',
                            'value': 'test@example.ru',
                            'string_value': 'test@example.ru',
                        },
                        'phone': {
                            'name': 'phone',
                            'type': 'phone',
                            'label': '',
                            'value': '79999999999',
                            'string_value': '79999999999',
                        },
                    },
                    'submitted_forms': [
                        {
                            'form_id': 10,
                            'answers': [
                                {
                                    'label': ' ?',
                                    'text': '',
                                    'meta': {
                                        'raw_value': '',
                                        'control_type': 'longText',
                                    },
                                },
                                {
                                    'label': ' ?',
                                    'text': (
                                        'https://kiosk-dev.vmb.co/private_read/forms/staging/1/'  # noqa: E501
                                        '56db2990-01fa-43da-9da4-06b13c272d15/qvV-0yZODfJVhzaCSFU7Aw.mp4'  # noqa: E501
                                    ),
                                    'meta': {
                                        'raw_value': [
                                            {
                                                'url': (
                                                    'https://kiosk-dev.vmb.co/private_read/forms/staging/'  # noqa: E501
                                                    '1/56db2990-01fa-43da-9da4-06b13c272d15/'  # noqa: E501
                                                    'qvV-0yZODfJVhzaCSFU7Aw.mp4'  # noqa: E501
                                                ),
                                                'size': 524740,
                                                'content_type': 'video/mp4',
                                                'original_filename': '.mp4',
                                            },
                                        ],
                                        'control_type': 'files',
                                    },
                                },
                                {
                                    'label': ' ?',
                                    'text': '',
                                    'meta': {
                                        'raw_value': '',
                                        'control_type': 'longText',
                                    },
                                },
                                {
                                    'label': ' ',
                                    'text': (
                                        'https://kiosk-dev.vmb.co/private_read/forms/staging/1/'  # noqa: E501
                                        '56db2990-01fa-43da-9da4-06b13c272d15/6-nq2iDTANC5P2QHqdznrQ.jpg'  # noqa: E501
                                    ),
                                    'meta': {
                                        'raw_value': [
                                            {
                                                'url': (
                                                    'https://kiosk-dev.vmb.co/private_read/forms/staging/1/'  # noqa: E501
                                                    '56db2990-01fa-43da-9da4-06b13c272d15/'  # noqa: E501
                                                    '6-nq2iDTANC5P2QHqdznrQ.jpg'  # noqa: E501
                                                ),
                                                'size': 130221,
                                                'content_type': 'image/jpeg',
                                                'original_filename': (
                                                    '87494-1-1508804254.jpg'
                                                ),
                                            },
                                        ],
                                        'control_type': 'files',
                                    },
                                },
                            ],
                        },
                    ],
                    'program': {
                        'uuid': '9e0e1163-0950-4d12-933c-665e21220a3c',
                        'name': '1',
                    },
                    'session_exams': [
                        {
                            'exam_state': 'finished',
                            'score': 2,
                            'min_score': 1,
                            'max_score': 2,
                            'grade_by': 'total_sections',
                            'answers': [
                                {
                                    'question': {
                                        'id': 73,
                                        'name': '1 + 1 + 2 + 3 = ?',
                                    },
                                    'answer_options': [
                                        {
                                            'id': 209,
                                            'name': '7',
                                            'correct': True,
                                        },
                                    ],
                                },
                                {
                                    'question': {
                                        'id': 74,
                                        'name': '5 + 4 + 1 = ?',
                                    },
                                    'answer_options': [
                                        {
                                            'id': 212,
                                            'name': '10',
                                            'correct': True,
                                        },
                                    ],
                                },
                                {
                                    'question': {
                                        'id': 73,
                                        'name': '1 + 1 + 2 + 3 = ?',
                                    },
                                    'answer_options': [
                                        {
                                            'id': 209,
                                            'name': '7',
                                            'correct': True,
                                        },
                                    ],
                                },
                            ],
                            'section_results': [
                                {
                                    'section_id': 88,
                                    'section_name': '1',
                                    'grade': '',
                                    'blocking': False,
                                    'score': 1,
                                    'max_score': 1,
                                    'min_score': 1,
                                    'passed': True,
                                },
                                {
                                    'section_id': 89,
                                    'section_name': '2',
                                    'grade': '',
                                    'blocking': False,
                                    'score': 2,
                                    'max_score': 2,
                                    'min_score': 1,
                                    'passed': True,
                                },
                            ],
                        },
                    ],
                },
            }

    return MockKiosk()


def pasport_headers(yandex_uid: typing.Optional[str]):
    if yandex_uid:
        return {'X-Yandex-UID': yandex_uid, 'X-Yandex-Login': 'user_login'}
    return {}
