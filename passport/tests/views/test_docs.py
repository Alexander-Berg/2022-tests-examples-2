# -*- coding: utf-8 -*-

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.test.base_test_case import BaseTestCase
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.permissions_mock import PermissionsMock
from passport.backend.vault.api.test.secrets_mock import SecretsMock
from passport.backend.vault.api.test.uuid_mock import UuidMock
from passport.backend.vault.api.views import validators
from passport.backend.vault.api.views.base_form import (
    BaseForm,
    StringField_,
)
from passport.backend.vault.api.views.base_view import BaseView
from passport.backend.vault.api.views.docs import DocsView
from passport.backend.vault.api.views.docs.views import parse_docstring
import wtforms


class _SubForm(BaseForm):
    name = StringField_(
        'Name for secret',
        description='non-unique name for the secret',
        validators=[
            validators.DataRequired(),
            validators.NAME_REGEXP_VALIDATOR,
            validators.Length(max=255),
        ],
    )
    comment = StringField_(
        'Comment',
        description='comment',
        strip=True,
        validators=[
            validators.Optional(),
            validators.Length(max=1023),
        ],
    )


class _EndpointForm(BaseForm):
    secrets = wtforms.FieldList(
        wtforms.FormField(
            _SubForm,
        ),
        label='Secrets',
        description='Max items: 100',
        validators=[
            validators.DataRequired(),
        ],
    )
    state = StringField_(
        'state',
        description='state',
        validators=[validators.Optional(), validators.AnyOf(['normal', 'hidden'])],
    )


class _EndpointView(BaseView):
    """
    Базовая ручка
    -----
    returns = ['secrets', 'status']
    raises = [DecryptionError]
    example = {
        'arguments': {
            '<string:secret_uuid>': 'sec-0000000000000000000000ygj0',
        },
        'data': '',
        'response': {
            'page': 0,
            'page_size': 50,
            'secrets': [{
                'effective_role': 'OWNER',
                'created_at': 1445385604,
                'created_by': 100,
                'creator_login': 'vault-test-100',
                'name': 'secret_2',
                'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                'secret_roles': [{
                    'role_slug': 'OWNER',
                    'uid': 100,
                    'created_at': 1445385604,
                    'created_by': 100,
                    'login': 'vault-test-100',
                    'creator_login': 'vault-test-100',
                }],
                'tokens_count': 0,
                'updated_at': 1445385608,
                'updated_by': 100,
                'uuid': 'sec-0000000000000000000000ygj5',
                'versions_count': 4,
            }],
            'status': 'ok',
        },
    }
    """
    required_user_auth = True
    form = _EndpointForm


class _UanuthorizedEndpointView(_EndpointView):
    required_user_auth = False


class _Rule(object):
    def __init__(self, methods=None, path='/', arguments=[]):
        self.methods = ['OPTIONS', 'HEAD', 'GET']
        self.path = path
        self.arguments = arguments

    def __str__(self):
        return self.path


class TestDocsViewMethods(BaseTestClass):
    """
    Тестируем методы класса DocsView, формирующие документацию
    """
    maxDiff = None

    def test_get_view_doc(self):
        dv = DocsView()
        self.assertDictEqual(
            dv.get_doc(_Rule(arguments=['id']), _EndpointView.as_view()),
            {'arguments': 'id',
             'description': '\xd0\x91\xd0\xb0\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x8f \xd1\x80\xd1\x83\xd1\x87\xd0\xba\xd0\xb0',
             'example': {'arguments': {'<string:secret_uuid>': 'sec-0000000000000000000000ygj0'},
                         'data': '',
                         'headers': {'X-Ya-User-Ticket': '<user_ticket>'},
                         'response': {'page': 0,
                                      'page_size': 50,
                                      'secrets': [{'created_at': 1445385604,
                                                   'created_by': 100,
                                                   'creator_login': 'vault-test-100',
                                                   'effective_role': 'OWNER',
                                                   'last_secret_version': {'version': 'ver-0000000000000000000000ygja'},
                                                   'name': 'secret_2',
                                                   'secret_roles': [{'created_at': 1445385604,
                                                                     'created_by': 100,
                                                                     'creator_login': 'vault-test-100',
                                                                     'login': 'vault-test-100',
                                                                     'role_slug': 'OWNER',
                                                                     'uid': 100}],
                                                   'tokens_count': 0,
                                                   'updated_at': 1445385608,
                                                   'updated_by': 100,
                                                   'uuid': 'sec-0000000000000000000000ygj5',
                                                   'versions_count': 4}],
                                      'status': 'ok'}},
             'form': {'secrets': {'form': {'comment': {'default': None,
                                                       'description': 'comment',
                                                       'list': False,
                                                       'validators': ['length: 1_to_1023']},
                                           'name': {'default': None,
                                                    'description': 'non-unique name for the secret',
                                                    'list': False,
                                                    'validators': ['required',
                                                                   'regexp: ^[a-zA-Z0-9_\\-\\.]+$',
                                                                   'length: 1_to_255']}},
                                  'list': True,
                                  'default': None,
                                  'description': 'Max items: 100',
                                  'validators': ['required']},
                      'state': {'default': None,
                                'description': 'state',
                                'list': False,
                                'validators': ["any_of: ['normal', 'hidden']"]}},
             'host': '',
             'method': 'GET',
             'path': '/',
             'raises': ['decryption_error',
                        'service_temporary_down',
                        'validation_error',
                        'access_error',
                        'invalid_oauth_token_error',
                        'invalid_scopes_error',
                        'login_header_in_rsa_signature_required_error',
                        'outdated_rsa_signature_error',
                        'rsa_signature_error',
                        'service_ticket_required_error',
                        'service_ticket_parsing_error',
                        'timestamp_header_in_rsa_signature_required_error',
                        'user_auth_required_error',
                        'user_ticket_parsing_error',
                        'zero_default_uid_error'],
             'required_user_auth': True,
             'returns': ['status', 'secrets']},
        )

    def test_get_unauthorized_endpoint_doc(self):
        dv = DocsView()
        self.assertDictEqual(
            dv.get_doc(_Rule(arguments=['id']), _UanuthorizedEndpointView.as_view()),
            {'arguments': 'id',
             'description': '',
             'example': {'headers': {}},
             'form': {'secrets': {'form': {'comment': {'default': None,
                                                       'description': 'comment',
                                                       'list': False,
                                                       'validators': ['length: 1_to_1023']},
                                           'name': {'default': None,
                                                    'description': 'non-unique name for the secret',
                                                    'list': False,
                                                    'validators': ['required',
                                                                   'regexp: ^[a-zA-Z0-9_\\-\\.]+$',
                                                                   'length: 1_to_255']}},
                                  'list': True,
                                  'default': None,
                                  'description': 'Max items: 100',
                                  'validators': ['required']},
                      'state': {'default': None,
                                'description': 'state',
                                'list': False,
                                'validators': ["any_of: ['normal', 'hidden']"]}},
             'host': '',
             'method': 'GET',
             'path': '/',
             'raises': ['service_temporary_down', 'validation_error'],
             'required_user_auth': False,
             'returns': ['status']},
        )


class TestDocsExamples(BaseTestClass):
    """
    Запускает пример из докстринга и проверяет результат
    """

    fill_database = False
    send_user_ticket = True
    maxDiff = None

    def setUp(self):
        super(TestDocsExamples, self).setUp()
        self.maxDiff = None
        self.fixture.fill_abc()
        self.fixture.fill_staff()
        self.fixture.fill_tvm_apps()
        self.fixture.fill_grants()

    def patch_path(self, path, arguments):
        for argument, value in arguments.items():
            path = path.replace(argument, value)
        return path

    def check_if_run_not_required(self, method, path):
        excluded_paths = {'/1/docs/', '/ping/', '/ping.html', '/'}
        return method.lower() != 'get' or path in excluded_paths

    def request_help(self):
        help = self.native_client.get('/1/docs/').json()['help']
        help_dict = {}
        for el in help:
            help_dict[(el['method'].lower(), el['path'])] = el
        return help_dict

    def do_request_method(self, data):
        request_method = getattr(self.native_client, data['method'].lower())
        request_path = self.patch_path(data['path'], data['example'].get('arguments', {}))
        request_data = data['example'].get('data', '')
        request_headers = data['example'].get('headers', {})
        if request_headers.get('Content-Type') == 'application/json':
            response = request_method(
                request_path,
                data=request_data,
                headers=request_headers,
                content_type='application/json',
            )
        else:
            response = request_method(
                request_path,
                query_string=request_data,
                headers=request_headers,
            )
        return response.json()

    def base_check(self, method, path):
        help_for_path = self.request_help()[(method, path)]
        with PermissionsMock(uid=100):
            with UuidMock():
                response = self.do_request_method(help_for_path)
                self.assertDictEqual(response, help_for_path['example']['response'])

    def test_get_methods(self):
        self.fixture.insert_data()
        with PermissionsMock(uid=100):
            with TimeMock():
                with UuidMock(base_value=700000):
                    with SecretsMock('gcwCk8kPz65Y54HnTrDKbjAN0FXAJPlnJVzpJtpRhwE'):
                        self.client.create_token(
                            tvm_client_id='2000367',
                            secret_uuid='sec-0000000000000000000000ygj0',
                            signature='123',
                        )
                    self.client.create_secret_version(
                        secret_uuid='sec-0000000000000000000000ygj0',
                        value=[
                            {'key': 'password', 'value': '123'},
                            {'key': 'cert', 'value': 'U2VjcmV0IGZpbGU=', 'encoding': 'base64'},
                        ],
                    )

        help = self.request_help()
        for method, path in help:
            if method == 'get':
                self.base_check(method, path)

    # def test_create_bundle(self):
    #     self.base_check('post', '/1/bundles/')

    # def test_update_bundle(self):
    #     self.fixture.insert_data()
    #     self.base_check('post', '/1/bundles/<string:bundle_uuid>/')

    def test_update_secret(self):
        self.fixture.insert_data()
        self.base_check('post', '/1/secrets/<string:secret_uuid>/')

    def test_create_secret(self):
        self.base_check('post', '/1/secrets/')

    def test_create_complete_secret(self):
        self.fixture.fill_abc()
        self.base_check('post', '/web/secrets/')

    def test_create_versions(self):
        help_for_path = self.request_help()[('post', '/1/secrets/<string:secret_uuid>/versions/')]
        with PermissionsMock(uid=100):
            with UuidMock():
                self.client.create_secret(name='secret_1')
                response = self.do_request_method(help_for_path)
            self.assertDictEqual(response, help_for_path['example']['response'])

    def test_tokens(self):
        help_for_path = self.request_help()[('post', '/1/secrets/<string:secret_uuid>/tokens/')]
        with PermissionsMock(uid=100):
            with UuidMock():
                self.client.create_secret(name='secret_1')
                with SecretsMock('gcwCk8kPz65Y54HnTrDKbjAN0FXAJPlnJVzpJtpRhwE'):
                    response = self.do_request_method(help_for_path)
            self.assertDictEqual(response, help_for_path['example']['response'])

    def test_roles(self):
        help_for_path = self.request_help()[('post', '/1/secrets/<string:secret_uuid>/roles/')]
        with PermissionsMock(uid=100):
            with UuidMock():
                self.client.create_secret(name='secret_1')
            response = self.do_request_method(help_for_path)
            self.assertDictEqual(response, help_for_path['example']['response'])

    def test_supervisors(self):
        help_for_path = self.request_help()[('post', '/1/supervisors/')]
        with PermissionsMock(uid=999, supervisor=True):
            self.client.add_supervisor(100)
        with PermissionsMock(uid=100):
            response = self.do_request_method(help_for_path)
            self.assertDictEqual(response, help_for_path['example']['response'])

    def test_invoke(self):
        help_for_path = self.request_help()[('post', '/1/tokens/')]
        with PermissionsMock(uid=100):
            with UuidMock():
                secret_uuid = self.client.create_secret(name='secret_1')
                self.client.create_secret_version(
                    secret_uuid=secret_uuid,
                    value=help_for_path['example']['response']['secrets'][1]['value'],
                )
                self.client.create_secret_version(
                    secret_uuid=secret_uuid,
                    value=help_for_path['example']['response']['secrets'][0]['value'],
                )
                with SecretsMock('gcwCk8kPz65Y54HnTrDKbjAN0FXAJPlnJVzpJtpRhwE'):
                    self.client.create_token(
                        secret_uuid=secret_uuid,
                        signature='123',
                    )
            response = self.do_request_method(help_for_path)
            self.assertDictEqual(response, help_for_path['example']['response'])

    def test_token_info(self):
        help_for_path = self.request_help()[('post', '/1/tokens/info/')]
        with PermissionsMock(uid=100):
            with TimeMock():
                with UuidMock(base_value=9000000):
                    secret_uuid = self.client.create_secret(name='secret_1')
                    with SecretsMock('gcwCk8kPz65Y54HnTrDKbjAN0FXAJPlnJVzpJtpRhwE'):
                        self.client.create_token(
                            secret_uuid=secret_uuid,
                            tvm_client_id='2000367',
                            signature='123',
                        )
        response = self.do_request_method(help_for_path)
        self.assertDictEqual(response, help_for_path['example']['response'])


class DocstringTestException(Exception):
    pass


class DocstringTestClass(object):
    """Undefined docstring"""
    def __init__(self, doc=None):
        if doc is not None:
            self.__doc__ = doc


VALID_DOCSTRINGS = [
    (
        DocstringTestClass(''),
        dict(description='', data={}),
    ),
    (
        DocstringTestClass('  Class description  \n  Second line'),
        dict(description='Class description  \nSecond line', data={}),
    ),
    (
        DocstringTestClass('  Class description  \n\n\n---\nreturns = ["error"]\nraises = [DocstringTestException, Exception]\nexamples = {"key": "value"}'),
        dict(
            description='Class description',
            data={
                'returns': ['error'],
                'raises': [DocstringTestException, Exception],
                'examples': {'key': 'value'},
            },
        ),
    ),
    (
        DocstringTestClass('    Class description\n    ---\n    returns = ["error"]\n    raises = [DocstringTestException, Exception]\n    examples = {"key": "value"}'),
        dict(
            description='Class description',
            data={
                'returns': ['error'],
                'raises': [DocstringTestException, Exception],
                'examples': {'key': 'value'},
            },
        ),
    ),
]

INVALID_DOCSTRINGS = [
    (
        DocstringTestClass('---\nreturns=["error"]\nraises=[Exception]\nexamples={}'),
        dict(
            description='---\nreturns=["error"]\nraises=[Exception]\nexamples={}',
            data={},
        ),
    ),
]


class TestDocstringParser(BaseTestCase):
    def test_test_docstring_class(self):
        doc = DocstringTestClass()
        self.assertEqual(doc.__doc__, 'Undefined docstring')

        doc = DocstringTestClass('New docstring')
        self.assertEqual(doc.__doc__, 'New docstring')

    def test_valid_docstrings(self):
        for doc in VALID_DOCSTRINGS:
            parsed = parse_docstring(doc[0])
            self.assertEqual(parsed, doc[1])

    def test_invalid_docstrings(self):
        for doc in INVALID_DOCSTRINGS:
            parsed = parse_docstring(doc[0])
            self.assertEqual(parsed, doc[1])
