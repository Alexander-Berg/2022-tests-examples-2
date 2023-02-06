# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from contextlib import contextmanager
from itertools import product
from operator import itemgetter

from nose_parameterized import parameterized
from passport.backend.core import Undefined
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.utils import insert_with_on_duplicate_key_update
from passport.backend.social.common.application import (
    Application,
    application_eav_configuration,
    ApplicationDatabaseReader,
    ApplicationModelDatabaseSerializer,
)
from passport.backend.social.common.db.schemas import (
    application_attribute_table,
    application_index_attribute_table,
    application_table,
)
from passport.backend.social.common.serialize import ValueSerializationError
from passport.backend.social.common.test.consts import (
    APPLICATION_ID3,
    APPLICATION_ID4,
    APPLICATION_NAME3,
    APPLICATION_NAME4,
    APPLICATION_SECRET1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    PROVIDER_ID3,
    PROVIDER_ID4,
)
from passport.backend.social.common.test.parameterized import name_parameterized_func
from passport.backend.social.common.test.test_case import TestCase
from sqlalchemy import and_ as sql_and


APPLICATION_ID1 = APPLICATION_ID3
APPLICATION_ID2 = APPLICATION_ID4
APPLICATION_NAME1 = APPLICATION_NAME3
APPLICATION_NAME2 = APPLICATION_NAME4
PROVIDER_ID1 = PROVIDER_ID3
PROVIDER_ID2 = PROVIDER_ID4


class _SerializationResult(object):
    def __init__(self, queries_gen):
        self.queries_gen = queries_gen


class _ApplicationDatabaseReaderTestCase(TestCase):
    all_known_attributes = dict(
        secret=APPLICATION_SECRET1,
        default_scope='scope1 scope2',
        authorization_url='authorization_url1',
        token_url='token_url1',
        refresh_token_url='refresh_token_url1',
        app_server_key='app_server_key1',
        key='key1',
        default='1',
        domain='domain1',
        engine_id='engine_id1',
        group_id='group_id1',
        is_third_party='1',
        related_yandex_client_id='related_yandex_client_id1',
        related_yandex_client_secret='related_yandex_client_secret1',
        tld='tld1;tld2;tld3',
    )

    def setUp(self):
        super(_ApplicationDatabaseReaderTestCase, self).setUp()
        self._loader = ApplicationDatabaseReader(self._fake_db.get_engine())

    def _create_application_in_database(self,
                                        application_id=APPLICATION_ID1,
                                        provider_id=PROVIDER_ID1,
                                        provider_client_id=EXTERNAL_APPLICATION_ID1,
                                        application_name=APPLICATION_NAME1,
                                        attr_name_to_value=None,
                                        attr_type_to_value=None):
        db = self._fake_db.get_engine()
        db.execute(
            application_table.insert().values(
                application_id=application_id,
                provider_id=provider_id,
                provider_client_id=provider_client_id,
                application_name=application_name,
            ),
        )
        self._create_application_attributes_in_database(
            application_id,
            attr_name_to_value,
            attr_type_to_value,
        )

    def _create_application_attributes_in_database(self,
                                                   application_id=APPLICATION_ID1,
                                                   attr_name_to_value=None,
                                                   attr_type_to_value=None):
        attr_name_to_value = attr_name_to_value or dict()
        attr_type_to_value = attr_type_to_value or dict()

        insert_records = []
        insert_index_records = []
        for attr_name, attr_value in attr_name_to_value.iteritems():
            if attr_name in application_eav_configuration.eav_attributes:
                insert_records.append(
                    dict(
                        application_id=application_id,
                        type=application_eav_configuration.eav_attributes[attr_name],
                        value=attr_value,
                    ),
                )
            else:
                insert_index_records.append(
                    dict(
                        application_id=application_id,
                        type=application_eav_configuration.eav_index_attributes[attr_name],
                        value=attr_value,
                    ),
                )
        for attr_type, attr_value in attr_type_to_value.iteritems():
            insert_records.append(
                dict(
                    application_id=application_id,
                    type=attr_type,
                    value=attr_value,
                ),
            )

        db = self._fake_db.get_engine()
        if insert_records:
            db.execute(application_attribute_table.insert(), insert_records)
        if insert_index_records:
            db.execute(application_index_attribute_table.insert(), insert_index_records)

    def _build_expected_app(self, attrs=None):
        attrs = attrs or dict()
        defaults = dict(
            application_id=APPLICATION_ID1,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
        )
        for key in defaults:
            attrs.setdefault(key, defaults[key])
        for attr_name, attr_value in attrs.iteritems():
            if not isinstance(attr_value, basestring):
                attrs[attr_name] = str(attr_value)
        return attrs


class TestApplicationDatabaseByApplicationIdsReader(_ApplicationDatabaseReaderTestCase):
    def test_application_not_found(self):
        self._create_application_in_database(application_id=APPLICATION_ID2)

        apps = self._loader.load_by_application_ids([APPLICATION_ID1])

        self.assertEqual(apps, [])

    def test_application_without_attributes(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
        )

        apps = self._loader.load_by_application_ids([APPLICATION_ID1])

        self.assertEqual(
            apps,
            [
                self._build_expected_app(
                    dict(
                        application_id=APPLICATION_ID1,
                        provider_id=PROVIDER_ID1,
                        provider_client_id=EXTERNAL_APPLICATION_ID1,
                        application_name=APPLICATION_NAME1,
                    ),
                ),
            ],
        )

    def test_application_with_all_known_attributes(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID2,
            attr_name_to_value=self.all_known_attributes,
        )

        apps = self._loader.load_by_application_ids([APPLICATION_ID2])

        expected_attrs = dict(self.all_known_attributes, application_id=APPLICATION_ID2)
        self.assertEqual(apps, [self._build_expected_app(expected_attrs)])

    def test_unknown_attribute(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID2,
            attr_type_to_value={9999: 'unknown'},
        )

        apps = self._loader.load_by_application_ids([APPLICATION_ID2])

        self.assertEqual(
            apps,
            [
                self._build_expected_app(dict(application_id=APPLICATION_ID2)),
            ],
        )

    def test_attribute_without_application(self):
        self._create_application_attributes_in_database(
            application_id=APPLICATION_ID2,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )

        apps = self._loader.load_by_application_ids([APPLICATION_ID2])

        self.assertEqual(apps, [])

    def test_many_applications(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )
        self._create_application_in_database(
            application_id=APPLICATION_ID2,
            provider_client_id=EXTERNAL_APPLICATION_ID2,
            application_name=APPLICATION_NAME2,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )

        apps = self._loader.load_by_application_ids([APPLICATION_ID1, APPLICATION_ID2])

        expected_apps = [
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    secret=APPLICATION_SECRET1,
                ),
            ),
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID2,
                    provider_client_id=EXTERNAL_APPLICATION_ID2,
                    application_name=APPLICATION_NAME2,
                    secret=APPLICATION_SECRET1,
                ),
            ),
        ]
        by_application_id = itemgetter('application_id')
        self.assertEqual(
            sorted(apps, key=by_application_id),
            sorted(expected_apps, key=by_application_id),
        )


class TestApplicationDatabaseByProviderIdsReader(_ApplicationDatabaseReaderTestCase):
    def test_application_not_found(self):
        self._create_application_in_database(provider_id=PROVIDER_ID2)

        apps = self._loader.load_by_provider_ids([PROVIDER_ID1])

        self.assertEqual(apps, [])

    def test_application_without_attributes(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
        )

        apps = self._loader.load_by_provider_ids([PROVIDER_ID1])

        self.assertEqual(
            apps,
            [
                self._build_expected_app(
                    dict(
                        application_id=APPLICATION_ID1,
                        provider_id=PROVIDER_ID1,
                        provider_client_id=EXTERNAL_APPLICATION_ID1,
                        application_name=APPLICATION_NAME1,
                    ),
                ),
            ],
        )

    def test_application_with_all_known_attributes(self):
        self._create_application_in_database(
            provider_id=PROVIDER_ID2,
            attr_name_to_value=self.all_known_attributes,
        )

        apps = self._loader.load_by_provider_ids([PROVIDER_ID2])

        expected_attrs = dict(self.all_known_attributes, provider_id=PROVIDER_ID2)
        self.assertEqual(apps, [self._build_expected_app(expected_attrs)])

    def test_unknown_attribute(self):
        self._create_application_in_database(
            provider_id=PROVIDER_ID2,
            attr_type_to_value={9999: 'unknown'},
        )

        apps = self._loader.load_by_provider_ids([PROVIDER_ID2])

        self.assertEqual(
            apps,
            [
                self._build_expected_app(dict(provider_id=PROVIDER_ID2)),
            ],
        )

    def test_many_applications_on_single_provider(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )
        self._create_application_in_database(
            application_id=APPLICATION_ID2,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID2,
            application_name=APPLICATION_NAME2,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )

        apps = self._loader.load_by_provider_ids([PROVIDER_ID1])

        expected_apps = [
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID1,
                    provider_id=PROVIDER_ID1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    secret=APPLICATION_SECRET1,
                ),
            ),
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID2,
                    provider_id=PROVIDER_ID1,
                    provider_client_id=EXTERNAL_APPLICATION_ID2,
                    application_name=APPLICATION_NAME2,
                    secret=APPLICATION_SECRET1,
                ),
            ),
        ]
        by_application_id = itemgetter('application_id')
        self.assertEqual(
            sorted(apps, key=by_application_id),
            sorted(expected_apps, key=by_application_id),
        )

    def test_many_application_on_many_providers(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )
        self._create_application_in_database(
            application_id=APPLICATION_ID2,
            provider_id=PROVIDER_ID2,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME2,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )

        apps = self._loader.load_by_provider_ids([PROVIDER_ID1, PROVIDER_ID2])

        expected_apps = [
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID1,
                    provider_id=PROVIDER_ID1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    secret=APPLICATION_SECRET1,
                ),
            ),
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID2,
                    provider_id=PROVIDER_ID2,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    application_name=APPLICATION_NAME2,
                    secret=APPLICATION_SECRET1,
                ),
            ),
        ]
        by_application_id = itemgetter('application_id')
        self.assertEqual(
            sorted(apps, key=by_application_id),
            sorted(expected_apps, key=by_application_id),
        )


class TestApplicationDatabaseByProviderClientIdsReader(_ApplicationDatabaseReaderTestCase):
    def test_application_not_found(self):
        self._create_application_in_database(
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID2,
        )

        apps = self._loader.load_by_provider_client_ids(
            [
                (PROVIDER_ID1, EXTERNAL_APPLICATION_ID1),
                (PROVIDER_ID2, EXTERNAL_APPLICATION_ID2),
            ],
        )

        self.assertEqual(apps, [])

    def test_application_without_attributes(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
        )

        apps = self._loader.load_by_provider_client_ids([(PROVIDER_ID1, EXTERNAL_APPLICATION_ID1)])

        self.assertEqual(
            apps,
            [
                self._build_expected_app(
                    dict(
                        application_id=APPLICATION_ID1,
                        provider_id=PROVIDER_ID1,
                        provider_client_id=EXTERNAL_APPLICATION_ID1,
                        application_name=APPLICATION_NAME1,
                    ),
                ),
            ],
        )

    def test_application_with_all_known_attributes(self):
        self._create_application_in_database(
            provider_id=PROVIDER_ID2,
            provider_client_id=EXTERNAL_APPLICATION_ID2,
            attr_name_to_value=self.all_known_attributes,
        )

        apps = self._loader.load_by_provider_client_ids([(PROVIDER_ID2, EXTERNAL_APPLICATION_ID2)])

        expected_attrs = dict(
            self.all_known_attributes,
            provider_id=PROVIDER_ID2,
            provider_client_id=EXTERNAL_APPLICATION_ID2,
        )
        self.assertEqual(apps, [self._build_expected_app(expected_attrs)])

    def test_unknown_attribute(self):
        self._create_application_in_database(
            provider_id=PROVIDER_ID2,
            provider_client_id=EXTERNAL_APPLICATION_ID2,
            attr_type_to_value={9999: 'unknown'},
        )

        apps = self._loader.load_by_provider_client_ids([(PROVIDER_ID2, EXTERNAL_APPLICATION_ID2)])

        self.assertEqual(
            apps,
            [
                self._build_expected_app(
                    dict(
                        provider_id=PROVIDER_ID2,
                        provider_client_id=EXTERNAL_APPLICATION_ID2,
                    ),
                ),
            ],
        )

    def test_many_applications(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )
        self._create_application_in_database(
            application_id=APPLICATION_ID2,
            provider_id=PROVIDER_ID2,
            provider_client_id=EXTERNAL_APPLICATION_ID2,
            application_name=APPLICATION_NAME2,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )

        apps = self._loader.load_by_provider_client_ids(
            [
                (PROVIDER_ID1, EXTERNAL_APPLICATION_ID1),
                (PROVIDER_ID2, EXTERNAL_APPLICATION_ID2),
            ],
        )

        expected_apps = [
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID1,
                    provider_id=PROVIDER_ID1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    secret=APPLICATION_SECRET1,
                ),
            ),
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID2,
                    provider_id=PROVIDER_ID2,
                    provider_client_id=EXTERNAL_APPLICATION_ID2,
                    application_name=APPLICATION_NAME2,
                    secret=APPLICATION_SECRET1,
                ),
            ),
        ]
        by_application_id = itemgetter('application_id')
        self.assertEqual(
            sorted(apps, key=by_application_id),
            sorted(expected_apps, key=by_application_id),
        )


class TestApplicationDatabaseByApplicationNamesReader(_ApplicationDatabaseReaderTestCase):
    def test_application_not_found(self):
        self._create_application_in_database(application_name=APPLICATION_NAME2)

        apps = self._loader.load_by_application_names([APPLICATION_NAME1])

        self.assertEqual(apps, [])

    def test_application_without_attributes(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_id=PROVIDER_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
        )

        apps = self._loader.load_by_application_names([APPLICATION_NAME1])

        self.assertEqual(
            apps,
            [
                self._build_expected_app(
                    dict(
                        application_id=APPLICATION_ID1,
                        provider_id=PROVIDER_ID1,
                        provider_client_id=EXTERNAL_APPLICATION_ID1,
                        application_name=APPLICATION_NAME1,
                    ),
                ),
            ],
        )

    def test_application_with_all_known_attributes(self):
        self._create_application_in_database(
            application_name=APPLICATION_NAME2,
            attr_name_to_value=self.all_known_attributes,
        )

        apps = self._loader.load_by_application_names([APPLICATION_NAME2])

        expected_attrs = dict(self.all_known_attributes, application_name=APPLICATION_NAME2)
        self.assertEqual(apps, [self._build_expected_app(expected_attrs)])

    def test_unknown_attribute(self):
        self._create_application_in_database(
            application_name=APPLICATION_NAME2,
            attr_type_to_value={9999: 'unknown'},
        )

        apps = self._loader.load_by_application_names([APPLICATION_NAME2])

        self.assertEqual(
            apps,
            [
                self._build_expected_app(dict(application_name=APPLICATION_NAME2)),
            ],
        )

    def test_many_applications(self):
        self._create_application_in_database(
            application_id=APPLICATION_ID1,
            provider_client_id=EXTERNAL_APPLICATION_ID1,
            application_name=APPLICATION_NAME1,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )
        self._create_application_in_database(
            application_id=APPLICATION_ID2,
            provider_client_id=EXTERNAL_APPLICATION_ID2,
            application_name=APPLICATION_NAME2,
            attr_name_to_value=dict(
                secret=APPLICATION_SECRET1,
            ),
        )

        apps = self._loader.load_by_application_names([APPLICATION_NAME1, APPLICATION_NAME2])

        expected_apps = [
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    secret=APPLICATION_SECRET1,
                ),
            ),
            self._build_expected_app(
                dict(
                    application_id=APPLICATION_ID2,
                    provider_client_id=EXTERNAL_APPLICATION_ID2,
                    application_name=APPLICATION_NAME2,
                    secret=APPLICATION_SECRET1,
                ),
            ),
        ]
        by_application_id = itemgetter('application_id')
        self.assertEqual(
            sorted(apps, key=by_application_id),
            sorted(expected_apps, key=by_application_id),
        )


class _ApplicationCreateDatabaseSerializerTestCase(TestCase):
    def setUp(self):
        super(_ApplicationCreateDatabaseSerializerTestCase, self).setUp()
        self._app = Application()

    def _assert_serialized_to_queries(self, expected):
        serializer = ApplicationModelDatabaseSerializer()
        queries_gen = serializer.serialize(None, self._app)
        eq_eav_queries(
            queries_gen,
            expected,
            inserted_keys=[APPLICATION_ID1]
        )

    def _assert_serialized_to_exception(self, exception_type, description):
        serializer = ApplicationModelDatabaseSerializer()

        with self.assertRaises(exception_type) as assertion:
            list(serializer.serialize(None, self._app))

        self.assertEqual(str(assertion.exception), description)


class TestApplicationIdentifierCreateDatabaseSerializer(_ApplicationCreateDatabaseSerializerTestCase):
    def test_undefined(self):
        self._app.identifier = Undefined
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )
        self.assertEqual(self._app.identifier, APPLICATION_ID1)

    def test_none(self):
        self._app.identifier = None
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )
        self.assertEqual(self._app.identifier, APPLICATION_ID1)

    def test_int(self):
        self._app.identifier = APPLICATION_ID1
        self._assert_serialized_to_queries(
            [
                application_table
                .insert()
                .values(
                    application_id=APPLICATION_ID1,
                    application_name=None,
                    provider_id=None,
                    provider_client_id=None,
                ),
            ],
        )
        self.assertEqual(self._app.identifier, APPLICATION_ID1)

    def test_invalid_type(self):
        self._app.identifier = 'x'
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: identifier = u'x'",
        )


class TestApplicationProviderCreateDatabaseSerializer(_ApplicationCreateDatabaseSerializerTestCase):
    def test_provider_undefined(self):
        self._app.provider = Undefined
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_provider_none(self):
        self._app.provider = None
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_provider_id_undefined(self):
        self._app.provider = dict(id=Undefined)
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: provider = {'id': Undefined}",
        )

    def test_provider_id_none(self):
        self._app.provider = dict(id=None)
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: provider = {'id': None}",
        )

    def test_provider_id_int(self):
        self._app.provider = dict(id=PROVIDER_ID1)
        self._assert_serialized_to_queries(
            [
                application_table
                .insert()
                .values(
                    application_name=None,
                    provider_id=PROVIDER_ID1,
                    provider_client_id=None,
                ),
            ],
        )

    def test_provider_id_0(self):
        self._app.provider = dict(id=0)
        self._assert_serialized_to_queries(
            [
                application_table
                .insert()
                .values(
                    application_name=None,
                    provider_id=0,
                    provider_client_id=None,
                ),
            ],
        )

    def test_provider_without_id(self):
        self._app.provider = dict(foo='bar')
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: provider = {'foo': u'bar'}",
        )

    def test_invalid_provider_type_true(self):
        self._app.provider = 5
        self._assert_serialized_to_exception(
            ValueSerializationError,
            'Invalid value: provider = 5',
        )

    def test_invalid_provider_type_false(self):
        self._app.provider = 0
        self._assert_serialized_to_exception(
            ValueSerializationError,
            'Invalid value: provider = 0',
        )

    def test_provider_id_invalid_type_true(self):
        self._app.provider = dict(id='x')
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: provider = {'id': u'x'}",
        )

    def test_provider_id_invalid_type_false(self):
        self._app.provider = dict(id='')
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: provider = {'id': u''}",
        )


class TestApplicationIdCreateDatabaseSerializer(_ApplicationCreateDatabaseSerializerTestCase):
    def test_undefined(self):
        self._app.id = Undefined
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_none(self):
        self._app.id = None
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_string(self):
        self._app.id = EXTERNAL_APPLICATION_ID1
        self._assert_serialized_to_queries(
            [
                application_table
                .insert()
                .values(
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    application_name=None,
                    provider_id=None,
                ),
            ],
        )

    def test_empty_string(self):
        self._app.id = ''
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_invalid_type_false(self):
        self._app.id = False
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: id = False",
        )

    def test_invalid_type_true(self):
        self._app.id = True
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: id = True",
        )


class TestApplicationNameCreateDatabaseSerializer(_ApplicationCreateDatabaseSerializerTestCase):
    def test_undefined(self):
        self._app.name = Undefined
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_none(self):
        self._app.name = None
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_string(self):
        self._app.name = APPLICATION_NAME1
        self._assert_serialized_to_queries(
            [
                application_table
                .insert()
                .values(
                    application_name=APPLICATION_NAME1,
                    provider_id=None,
                    provider_client_id=None,
                ),
            ],
        )

    def test_empty_string(self):
        self._app.name = ''
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_invalid_type_false(self):
        self._app.name = False
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: name = False",
        )

    def test_invalid_type_true(self):
        self._app.name = True
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: name = True",
        )


class TestApplicationSecretCreateDatabaseSerializer(_ApplicationCreateDatabaseSerializerTestCase):
    def test_undefined(self):
        self._app.secret = Undefined
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_none(self):
        self._app.secret = None
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_string(self):
        self._app.secret = '5ecre+'
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('secret'),
                        value='5ecre+',
                    )
                ),
            ],
        )

    def test_empty_string(self):
        self._app.secret = ''
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_invalid_type_false(self):
        self._app.secret = False
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: secret = False",
        )

    def test_invalid_type_true(self):
        self._app.secret = True
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: secret = True",
        )


class TestApplicationDefaultCreateDatabaseSerializer(_ApplicationCreateDatabaseSerializerTestCase):
    def test_undefined(self):
        self._app.default = Undefined
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_none(self):
        self._app.default = None
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_false(self):
        self._app.default = False
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_true(self):
        self._app.default = True
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('default'),
                        value='1',
                    )
                ),
            ],
        )

    def test_invalid_type_false(self):
        self._app.default = 0
        self._assert_serialized_to_exception(
            ValueSerializationError,
            'Invalid value: default = 0',
        )

    def test_invalid_type_true(self):
        self._app.default = '0'
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: default = u'0'",
        )


class TestApplicationTldCreateDatabaseSerializer(_ApplicationCreateDatabaseSerializerTestCase):
    def test_undefined(self):
        self._app.tld = Undefined
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_none(self):
        self._app.tld = None
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_empty_list(self):
        self._app.tld = []
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
            ],
        )

    def test_list_with_single_item(self):
        self._app.tld = ['x']
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('tld'),
                        value='x',
                    )
                ),
            ],
        )

    def test_list_with_many_items(self):
        self._app.tld = ['y', 'x', 'z']
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('tld'),
                        value='y;x;z',
                    )
                ),
            ],
        )

    def test_invalid_type_false(self):
        self._app.tld = False
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = False",
        )

    def test_invalid_type_true(self):
        self._app.tld = True
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = True",
        )

    def test_list_item_undefined(self):
        self._app.tld = [Undefined]
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = [Undefined]",
        )

    def test_list_item_none(self):
        self._app.tld = [None]
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = [None]",
        )

    def test_invalid_list_item_type_false(self):
        self._app.tld = [0]
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = [0]",
        )

    def test_invalid_list_item_type_true(self):
        self._app.tld = [1]
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = [1]",
        )

    def test_list_item_many_single_strings(self):
        self._app.tld = ['']
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('tld'),
                        value='',
                    )
                ),
            ],
        )

    def test_list_item_many_empty_strings(self):
        self._app.tld = ['', '']
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('tld'),
                        value=';',
                    )
                ),
            ],
        )

    def test_set(self):
        self._app.tld = set(['y', 'x', 'z'])
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('tld'),
                        value='x;y;z',
                    )
                ),
            ],
        )

    def test_tuple(self):
        self._app.tld = ('y', 'x', 'z')
        self._assert_serialized_to_queries(
            [
                application_table.insert().values(application_name=None, provider_id=None, provider_client_id=None),
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('tld'),
                        value='y;x;z',
                    )
                ),
            ],
        )

    def test_invalid_type_dict(self):
        self._app.tld = dict(x='y')
        self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = {'x': u'y'}",
        )

    def test_semicolon(self):
        self._app.tld = [';']
        self._assert_serialized_to_exception(NotImplementedError, '')


class TestApplicationIdentifierChangeDatabaseSerializer(TestCase):
    def test(self):
        app = Application()
        app.identifier = APPLICATION_ID1
        snapshot1 = app.snapshot()
        app.identifier = APPLICATION_ID2
        snapshot2 = app.snapshot()

        serializer = ApplicationModelDatabaseSerializer()

        with self.assertRaises(NotImplementedError):
            list(serializer.serialize(snapshot1, snapshot2))


class ApplicationChangeDatabaseSerializerTestCase(TestCase):
    def setUp(self):
        super(ApplicationChangeDatabaseSerializerTestCase, self).setUp()
        self._app = Application()
        self._app.identifier = APPLICATION_ID1

    @contextmanager
    def _serialize(self):
        result = _SerializationResult(None)
        snapshot1 = self._app.snapshot()
        yield result
        snapshot2 = self._app.snapshot()
        serializer = ApplicationModelDatabaseSerializer()
        result.queries_gen = serializer.serialize(snapshot1, snapshot2)

    @contextmanager
    def _assert_serialized_to_exception(self, exception_type, description):
        snapshot1 = self._app.snapshot()
        yield
        snapshot2 = self._app.snapshot()
        serializer = ApplicationModelDatabaseSerializer()
        with self.assertRaises(exception_type) as assertion:
            list(serializer.serialize(snapshot1, snapshot2))
        self.assertEqual(str(assertion.exception), description)


class TestApplicationProviderChangeDatabaseSerializer(ApplicationChangeDatabaseSerializerTestCase):
    valid_values = [
        Undefined,
        None,
        dict(id=PROVIDER_ID1),
        dict(id=0),
    ]
    invalid_values = [
        dict(id=Undefined),
        dict(id=None),
        dict(foo='bar'),
        0,
        5,
        dict(id=''),
        dict(id='x'),
    ]

    @parameterized.expand(product(valid_values, invalid_values), name_parameterized_func)
    def test_valid_to_invalid(self, valid_value, invalid_value):
        self._app.provider = valid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: provider = " + repr(invalid_value),
        ):
            self._app.provider = invalid_value

    @parameterized.expand(
        product(invalid_values, valid_values + invalid_values),
        name_parameterized_func,
    )
    def test_invalid_to_any(self, invalid_value, value):
        self._app.provider = invalid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: provider = " + repr(invalid_value),
        ):
            self._app.provider = value

    @parameterized.expand(
        [
            (Undefined, Undefined),
            (Undefined, None),
            (None, None),
            (None, Undefined),
            (dict(id=PROVIDER_ID1), dict(id=PROVIDER_ID1)),
            (dict(id=0), dict(id=0)),
        ],
        name_parameterized_func,
    )
    def test_valid_values_equal(self, value1, value2):
        self._app.provider = value1

        with self._serialize() as s:
            self._app.provider = value2

        eq_eav_queries(s.queries_gen, [])

    @parameterized.expand(
        [
            (Undefined, dict(id=PROVIDER_ID1), PROVIDER_ID1),
            (Undefined, dict(id=0), 0),
            (None, dict(id=PROVIDER_ID1), PROVIDER_ID1),
            (None, dict(id=0), 0),
            (dict(id=PROVIDER_ID1), dict(id=0), 0),
            (dict(id=0), dict(id=PROVIDER_ID1), PROVIDER_ID1),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_not_empty_valid_value(self, value1, value2, db_value):
        self._app.provider = value1

        with self._serialize() as s:
            self._app.provider = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    application_table
                    .update()
                    .values(provider_id=db_value)
                    .where(application_table.c.application_id == APPLICATION_ID1)
                ),
            ],
        )

    @parameterized.expand(
        [
            (dict(id=PROVIDER_ID1), Undefined),
            (dict(id=PROVIDER_ID1), None),
            (dict(id=0), Undefined),
            (dict(id=0), None),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_empty_valid_value(self, value1, value2):
        self._app.provider = value1

        with self._serialize() as s:
            self._app.provider = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    application_table
                    .update()
                    .values(provider_id=None)
                    .where(application_table.c.application_id == APPLICATION_ID1)
                ),
            ],
        )


class TestApplicationIdChangeDatabaseSerializer(ApplicationChangeDatabaseSerializerTestCase):
    valid_values = [
        Undefined,
        None,
        '',
        'hello',
    ]
    invalid_values = [
        True,
        False,
    ]

    @parameterized.expand(product(valid_values, invalid_values), name_parameterized_func)
    def test_valid_to_invalid(self, valid_value, invalid_value):
        self._app.id = valid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: id = " + repr(invalid_value),
        ):
            self._app.id = invalid_value

    @parameterized.expand(
        product(invalid_values, valid_values + invalid_values),
        name_parameterized_func,
    )
    def test_invalid_to_any_value(self, invalid_value, value):
        self._app.id = invalid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: id = " + repr(invalid_value),
        ):
            self._app.id = value

    @parameterized.expand(
        [
            (Undefined, Undefined),
            (Undefined, None),
            (Undefined, ''),
            (None, Undefined),
            (None, None),
            (None, ''),
            ('', Undefined),
            ('', None),
            ('', ''),
            ('hello', 'hello'),
        ],
        name_parameterized_func,
    )
    def test_valid_values_equal(self, value1, value2):
        self._app.id = value1

        with self._serialize() as s:
            self._app.id = value2

        eq_eav_queries(s.queries_gen, [])

    @parameterized.expand(
        [
            (Undefined, 'hello'),
            (None, 'hello'),
            ('', 'hello'),
            ('hello1', 'hello2'),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_not_empty_valid_value(self, value1, value2):
        self._app.id = value1

        with self._serialize() as s:
            self._app.id = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    application_table
                    .update()
                    .values(provider_client_id=value2)
                    .where(application_table.c.application_id == APPLICATION_ID1)
                ),
            ],
        )

    @parameterized.expand(
        [
            ('x', Undefined),
            ('x', None),
            ('x', ''),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_empty_valid_value(self, value1, value2):
        self._app.id = value1

        with self._serialize() as s:
            self._app.id = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    application_table
                    .update()
                    .values(provider_client_id=None)
                    .where(application_table.c.application_id == APPLICATION_ID1)
                ),
            ],
        )


class TestApplicationNameChangeDatabaseSerializer(ApplicationChangeDatabaseSerializerTestCase):
    valid_values = [
        Undefined,
        None,
        '',
        'hello',
    ]
    invalid_values = [
        True,
        False,
    ]

    @parameterized.expand(product(valid_values, invalid_values), name_parameterized_func)
    def test_valid_to_invalid(self, valid_value, invalid_value):
        self._app.name = valid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: name = " + repr(invalid_value),
        ):
            self._app.name = invalid_value

    @parameterized.expand(
        product(invalid_values, valid_values + invalid_values),
        name_parameterized_func,
    )
    def test_invalid_to_any_value(self, invalid_value, value):
        self._app.name = invalid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: name = " + repr(invalid_value),
        ):
            self._app.name = value

    @parameterized.expand(
        [
            (Undefined, Undefined),
            (Undefined, None),
            (Undefined, ''),
            (None, Undefined),
            (None, None),
            (None, ''),
            ('', Undefined),
            ('', None),
            ('', ''),
            ('hello', 'hello'),
        ],
        name_parameterized_func,
    )
    def test_valid_values_equal(self, value1, value2):
        self._app.name = value1

        with self._serialize() as s:
            self._app.name = value2

        eq_eav_queries(s.queries_gen, [])

    @parameterized.expand(
        [
            (Undefined, 'hello'),
            (None, 'hello'),
            ('', 'hello'),
            ('hello1', 'hello2'),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_not_empty_valid_value(self, value1, value2):
        self._app.name = value1

        with self._serialize() as s:
            self._app.name = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    application_table
                    .update()
                    .values(application_name=value2)
                    .where(application_table.c.application_id == APPLICATION_ID1)
                ),
            ],
        )

    @parameterized.expand(
        [
            ('x', Undefined),
            ('x', None),
            ('x', ''),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_empty_valid_value(self, value1, value2):
        self._app.name = value1

        with self._serialize() as s:
            self._app.name = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    application_table
                    .update()
                    .values(application_name=None)
                    .where(application_table.c.application_id == APPLICATION_ID1)
                ),
            ],
        )


class TestApplicationSecretChangeDatabaseSerializer(ApplicationChangeDatabaseSerializerTestCase):
    valid_values = [
        Undefined,
        None,
        '',
        'hello',
    ]
    invalid_values = [
        True,
        False,
    ]

    @parameterized.expand(product(valid_values, invalid_values), name_parameterized_func)
    def test_valid_to_invalid(self, valid_value, invalid_value):
        self._app.secret = valid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: secret = " + repr(invalid_value),
        ):
            self._app.secret = invalid_value

    @parameterized.expand(
        product(invalid_values, valid_values + invalid_values),
        name_parameterized_func,
    )
    def test_invalid_to_any_value(self, invalid_value, value):
        self._app.secret = invalid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: secret = " + repr(invalid_value),
        ):
            self._app.secret = value

    @parameterized.expand(
        [
            (Undefined, Undefined),
            (Undefined, None),
            (Undefined, ''),
            (None, Undefined),
            (None, None),
            (None, ''),
            ('', Undefined),
            ('', None),
            ('', ''),
            ('hello', 'hello'),
        ],
        name_parameterized_func,
    )
    def test_valid_values_equal(self, value1, value2):
        self._app.secret = value1

        with self._serialize() as s:
            self._app.secret = value2

        eq_eav_queries(s.queries_gen, [])

    @parameterized.expand(
        [
            (Undefined, 'hello'),
            (None, 'hello'),
            ('', 'hello'),
            ('hello1', 'hello2'),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_not_empty_valid_value(self, value1, value2):
        self._app.secret = value1

        with self._serialize() as s:
            self._app.secret = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('secret'),
                        value=value2,
                    )
                ),
            ],
        )

    @parameterized.expand(
        [
            ('x', Undefined),
            ('x', None),
            ('x', ''),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_empty_valid_value(self, value1, value2):
        self._app.secret = value1

        with self._serialize() as s:
            self._app.secret = value2

        eq_eav_queries(
            s.queries_gen,
            [
                application_attribute_table
                .delete()
                .where(
                    sql_and(
                        application_attribute_table.c.application_id == APPLICATION_ID1,
                        application_attribute_table.c.type.in_(
                            [
                                application_eav_configuration.get_type_from_name('secret'),
                            ],
                        ),
                    ),
                ),
            ],
        )


class TestApplicationDefaultChangeDatabaseSerializer(ApplicationChangeDatabaseSerializerTestCase):
    valid_values = [
        Undefined,
        None,
        False,
        True,
    ]
    invalid_values = [0, '0']

    @parameterized.expand(product(valid_values, invalid_values), name_parameterized_func)
    def test_valid_to_invalid(self, valid_value, invalid_value):
        self._app.default = valid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: default = " + repr(invalid_value),
        ):
            self._app.default = invalid_value

    @parameterized.expand(
        product(invalid_values, valid_values + invalid_values),
        name_parameterized_func,
    )
    def test_invalid_to_any_value(self, invalid_value, value):
        self._app.default = invalid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: default = " + repr(invalid_value),
        ):
            self._app.default = value

    @parameterized.expand(
        [
            (Undefined, Undefined),
            (Undefined, None),
            (Undefined, False),
            (None, Undefined),
            (None, None),
            (None, False),
            (False, Undefined),
            (False, None),
            (False, False),
            (True, True),
        ],
        name_parameterized_func,
    )
    def test_valid_values_equal(self, value1, value2):
        self._app.default = value1

        with self._serialize() as s:
            self._app.default = value2

        eq_eav_queries(s.queries_gen, [])

    @parameterized.expand(
        [
            (Undefined, True),
            (None, True),
            (False, True),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_not_empty_valid_value(self, value1, value2):
        self._app.default = value1

        with self._serialize() as s:
            self._app.default = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('default'),
                        value='1',
                    )
                ),
            ],
        )

    @parameterized.expand(
        [
            (True, Undefined),
            (True, None),
            (True, False),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_empty_valid_value(self, value1, value2):
        self._app.default = value1

        with self._serialize() as s:
            self._app.default = value2

        eq_eav_queries(
            s.queries_gen,
            [
                application_attribute_table
                .delete()
                .where(
                    sql_and(
                        application_attribute_table.c.application_id == APPLICATION_ID1,
                        application_attribute_table.c.type.in_(
                            [
                                application_eav_configuration.get_type_from_name('default'),
                            ],
                        ),
                    ),
                ),
            ],
        )


class TestApplicationTldChangeDatabaseSerializer(ApplicationChangeDatabaseSerializerTestCase):
    valid_values = [
        Undefined,
        None,
        list(),
        ['x'],
        ['y', 'x', 'z'],
        [''],
        ['', ''],
        {'y', 'x', 'z'},
        ('y', 'x', 'z'),
    ]
    invalid_values = [
        False,
        True,
        [Undefined],
        [None],
        [0],
        [1],
        dict(x='y'),
    ]

    @parameterized.expand(product(valid_values, invalid_values), name_parameterized_func)
    def test_valid_to_invalid(self, valid_value, invalid_value):
        self._app.tld = valid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = " + repr(invalid_value),
        ):
            self._app.tld = invalid_value

    @parameterized.expand(
        product(invalid_values, valid_values + invalid_values),
        name_parameterized_func,
    )
    def test_invalid_to_any_value(self, invalid_value, value):
        self._app.tld = invalid_value

        with self._assert_serialized_to_exception(
            ValueSerializationError,
            "Invalid value: tld = " + repr(invalid_value),
        ):
            self._app.tld = value

    @parameterized.expand(
        [
            (Undefined, Undefined),
            (Undefined, None),
            (Undefined, list()),
            (None, Undefined),
            (None, None),
            (None, list()),
            (list(), Undefined),
            (list(), None),
            (list(), list()),
            (['x'], ['x']),
            ([''], ['']),
            (['y', 'x', 'z'], ['y', 'x', 'z']),
            (['y', 'x', 'z'], ('y', 'x', 'z')),
            (['x', 'y', 'z'], {'y', 'x', 'z'}),
            ({'y', 'x', 'z'}, {'y', 'x', 'z'}),
            ({'y', 'x', 'z'}, ['x', 'y', 'z']),
            ({'y', 'x', 'z'}, ('x', 'y', 'z')),
            (('y', 'x', 'z'), ['y', 'x', 'z']),
            (('y', 'x', 'z'), ('y', 'x', 'z')),
            (('x', 'y', 'z'), {'y', 'x', 'z'}),
        ],
        name_parameterized_func,
    )
    def test_valid_values_equal(self, value1, value2):
        self._app.tld = value1

        with self._serialize() as s:
            self._app.tld = value2

        eq_eav_queries(s.queries_gen, [])

    @parameterized.expand(
        [
            (Undefined, ['xy'], 'xy'),
            (Undefined, ['y', 'x', 'z'], 'y;x;z'),
            (Undefined, ('y', 'x', 'z'), 'y;x;z'),
            (Undefined, {'y', 'x', 'z'}, 'x;y;z'),
            (Undefined, [''], ''),
            (Undefined, ['', ''], ';'),
            (None, ['xy'], 'xy'),
            (list(), ['xy'], 'xy'),
            (['xy'], ['y', 'x', 'z'], 'y;x;z'),
            (['xy'], [''], ''),
            (['xy'], ['', ''], ';'),
            (['y', 'x', 'z'], ['xy'], 'xy'),
            (['y', 'x', 'z'], {'y', 'x', 'z'}, 'x;y;z'),
            (['y', 'x', 'z'], [''], ''),
            (['y', 'x', 'z'], ['', ''], ';'),
            (('y', 'x', 'z'), {'y', 'x', 'z'}, 'x;y;z'),
            ({'y', 'x', 'z'}, ['y', 'x', 'z'], 'y;x;z'),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_not_empty_valid_value(self, value1, value2, db_value):
        self._app.tld = value1

        with self._serialize() as s:
            self._app.tld = value2

        eq_eav_queries(
            s.queries_gen,
            [
                (
                    insert_with_on_duplicate_key_update(
                        application_attribute_table,
                        ['value'],
                    )
                    .values(
                        application_id=APPLICATION_ID1,
                        type=application_eav_configuration.get_type_from_name('tld'),
                        value=db_value,
                    )
                ),
            ],
        )

    @parameterized.expand(
        [
            (['x'], Undefined),
            (['x'], None),
            (['x'], list()),
            (['y', 'x', 'z'], Undefined),
            (['y', 'x', 'z'], None),
            (['y', 'x', 'z'], list()),
            ([''], Undefined),
            ([''], None),
            ([''], list()),
        ],
        name_parameterized_func,
    )
    def test_valid_value_to_empty_valid_value(self, value1, value2):
        self._app.tld = value1

        with self._serialize() as s:
            self._app.tld = value2

        eq_eav_queries(
            s.queries_gen,
            [
                application_attribute_table
                .delete()
                .where(
                    sql_and(
                        application_attribute_table.c.application_id == APPLICATION_ID1,
                        application_attribute_table.c.type.in_(
                            [
                                application_eav_configuration.get_type_from_name('tld'),
                            ],
                        ),
                    ),
                ),
            ],
        )

    @parameterized.expand([(v,) for v in valid_values], name_parameterized_func)
    def test_valid_value_to_semicolon(self, value):
        self._app.tld = value

        with self._assert_serialized_to_exception(NotImplementedError, ''):
            self._app.tld = [';']


class TestApplicationDeleteDatabaseSerializer(TestCase):
    def setUp(self):
        super(TestApplicationDeleteDatabaseSerializer, self).setUp()
        self._app = Application(
            identifier=APPLICATION_ID1,
            name=APPLICATION_NAME1,
            provider=dict(id=PROVIDER_ID1),
            id=EXTERNAL_APPLICATION_ID1,
            secret='5ecr3+',
            default=True,
            tld=['ru'],
        )

    def _assert_model_reset(self):
        self.assertIs(self._app.identifier, Undefined)
        self.assertIs(self._app.name, Undefined)
        self.assertIs(self._app.provider, Undefined)
        self.assertIs(self._app.id, Undefined)
        self.assertIs(self._app.secret, Undefined)
        self.assertIs(self._app.default, Undefined)
        self.assertEqual(self._app.tld, [])

    def _assert_application_deleted(self, queries_gen):
        eq_eav_queries(
            queries_gen,
            [
                (
                    application_table.delete()
                    .where(application_table.c.application_id == APPLICATION_ID1)
                ),
                (
                    application_attribute_table.delete()
                    .where(application_attribute_table.c.application_id == APPLICATION_ID1)
                ),
                (
                    application_index_attribute_table.delete()
                    .where(application_index_attribute_table.c.application_id == APPLICATION_ID1)
                ),
            ],
        )

    def _delete(self):
        serializer = ApplicationModelDatabaseSerializer()
        return serializer.serialize(self._app, None)

    def test_without_identifier(self):
        self._app.identifier = Undefined

        queries_gen = self._delete()

        eq_eav_queries(queries_gen, [])
        self._assert_model_reset()

    def test_with_identifier(self):
        self._app.identifier = APPLICATION_ID1

        queries_gen = self._delete()

        self._assert_application_deleted(queries_gen)
        self._assert_model_reset()

    def test_identifier_defined_to_identifier_undefined(self):
        app = Application()
        app.identifier = APPLICATION_ID1
        snapshot1 = app.snapshot()
        app.identifier = Undefined
        snapshot2 = app.snapshot()

        serializer = ApplicationModelDatabaseSerializer()
        with self.assertRaises(NotImplementedError):
            list(serializer.serialize(snapshot1, snapshot2))
