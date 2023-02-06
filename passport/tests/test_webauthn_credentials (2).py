# -*- coding: utf-8 -*-
import unittest

from nose.tools import raises
from passport.backend.core.db.faker.db import (
    extended_attribute_table_delete as eat_delete,
    extended_attribute_table_insert_on_duplicate_key as eat_insert_odk,
    IdGeneratorFaker,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    extended_attributes_table as eat,
    webauthn_credentials_table as wct,
)
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_WEBAUTHN_NAME_TO_TYPE_MAPPING as EXT_ATTR_WEBAUTHN,
    EXTENDED_ATTRIBUTES_WEBAUTHN_TYPE,
)
from passport.backend.core.models.account import Account
from passport.backend.core.models.webauthn import WebauthnCredential
from passport.backend.core.serializers.eav.webauthn import (
    WebauthnCredentialEavSerializer,
    WebauthnCredentialsEavSerializer,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import merge_dicts
from sqlalchemy.sql.expression import and_


TEST_ENTITY_ID = 1
TEST_UID = 123

TEST_EXTERNAL_ID = 'external-id'
TEST_PUBLIC_KEY = 'public-key'
TEST_DEVICE_NAME = 'device-name'
TEST_RP_ID = 'rp-id'


class BaseWebauthnCredentialSerializeTestCase(unittest.TestCase):
    serializer_class = None

    def setUp(self):
        super(BaseWebauthnCredentialSerializeTestCase, self).setUp()
        self.id_faker = IdGeneratorFaker()
        self.id_faker.set_list(range(1, 100))
        self.id_faker.start()

        self.acc = Account(uid=TEST_UID).parse({})

    def tearDown(self):
        self.id_faker.stop()
        del self.id_faker

    def serialize(self, s1, s2):
        return self.serializer_class().serialize(
            s1,
            s2,
            diff(s1, s2),
        )

    def create(self, instance):
        return self.serialize(None, instance)

    def update(self, s1, instance):
        return self.serialize(s1, instance)

    def delete(self, instance):
        return self.serialize(instance, None)

    def eat_entry(self, **kwargs):
        base_entry = {
            'entity_id': TEST_ENTITY_ID,
            'entity_type': EXTENDED_ATTRIBUTES_WEBAUTHN_TYPE,
            'uid': TEST_UID,
        }
        return merge_dicts(base_entry, kwargs)


class TestSerializeWebauthnCredential(BaseWebauthnCredentialSerializeTestCase):
    serializer_class = WebauthnCredentialEavSerializer

    def test_create_ok(self):
        cred = WebauthnCredential(
            external_id=TEST_EXTERNAL_ID,
            public_key=TEST_PUBLIC_KEY,
            relying_party_id=TEST_RP_ID,
            device_name=TEST_DEVICE_NAME,
            os_family_id=10,
            browser_id=11,
            is_device_mobile=True,
            is_device_tablet=True,
            sign_count=1,
            created_at=DatetimeNow(),
        )
        self.acc.webauthn_credentials.add(cred)
        eq_eav_queries(
            self.create(cred),
            [
                eat_insert_odk().values([
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['external_id'],
                        value=TEST_EXTERNAL_ID.encode('utf8'),
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['public_key'],
                        value=b'1:%s' % TEST_PUBLIC_KEY.encode('utf8'),
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['device_name'],
                        value=TEST_DEVICE_NAME.encode('utf8'),
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['sign_count'],
                        value=b'1',
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['created'],
                        value=TimeNow(),
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['relying_party_id'],
                        value=TEST_RP_ID.encode('utf8'),
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['os_family_id'],
                        value=b'10',
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['browser_id'],
                        value=b'11',
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['is_device_mobile'],
                        value=b'1',
                    ),
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['is_device_tablet'],
                        value=b'1',
                    ),
                ]),
                wct.insert().values(uid=TEST_UID, credential_id=TEST_EXTERNAL_ID.encode('utf8')),
            ],
        )

    def test_update_sign_count(self):
        cred = WebauthnCredential(
            external_id=TEST_EXTERNAL_ID,
            public_key=TEST_PUBLIC_KEY,
            sign_count=1,
        )
        self.acc.webauthn_credentials.add(cred)
        cred.id = TEST_ENTITY_ID
        s1 = cred.snapshot()

        cred.sign_count = 2

        eq_eav_queries(
            self.update(s1, cred),
            [
                eat_insert_odk().values(
                    [
                        self.eat_entry(
                            type=EXT_ATTR_WEBAUTHN['sign_count'],
                            value=b'2',
                        ),
                    ],
                ),
            ],
        )

    def test_delete_single_cred(self):
        cred = WebauthnCredential(
            external_id=TEST_EXTERNAL_ID,
            public_key=TEST_PUBLIC_KEY,
            sign_count=1,
        )
        self.acc.webauthn_credentials.add(cred)
        cred.id = TEST_ENTITY_ID

        eq_eav_queries(
            self.delete(cred),
            [
                wct.delete().where(
                    and_(
                        wct.c.uid == TEST_UID,
                        wct.c.credential_id == TEST_EXTERNAL_ID.encode(),
                    ),
                ),
                eat_delete().where(
                    and_(
                        eat.c.uid == TEST_UID,
                        eat.c.entity_id == TEST_ENTITY_ID,
                        eat.c.entity_type == EXTENDED_ATTRIBUTES_WEBAUTHN_TYPE,
                    ),
                ),
            ],
        )

    def test_nothing_to_do(self):
        eq_eav_queries(
            self.serialize(None, None),
            [],
        )

    @raises(ValueError)
    def test_error_create_cred_without_external_id(self):
        cred = WebauthnCredential()

        eq_eav_queries(
            self.create(cred),
            [],
        )

    @raises(ValueError)
    def test_error_change_external_id(self):
        cred = WebauthnCredential(external_id=TEST_EXTERNAL_ID)
        s1 = cred.snapshot()

        cred.external_id = 'smth-other'

        eq_eav_queries(
            self.update(s1, cred),
            [],
        )


class TestSerializeWebauthnCredentialsList(BaseWebauthnCredentialSerializeTestCase):
    serializer_class = WebauthnCredentialsEavSerializer

    def test_empty_list_no_queries(self):
        eq_eav_queries(
            self.create(self.acc.webauthn_credentials),
            [],
        )

        eq_eav_queries(
            self.update(self.acc.webauthn_credentials, self.acc.webauthn_credentials),
            [],
        )

        eq_eav_queries(
            self.delete(self.acc.webauthn_credentials),
            [],
        )

    def test_add_cred(self):
        cred = WebauthnCredential(external_id=TEST_EXTERNAL_ID)
        self.acc.webauthn_credentials.add(cred)

        eq_eav_queries(
            self.create(self.acc.webauthn_credentials),
            [
                eat_insert_odk().values(
                    self.eat_entry(
                        type=EXT_ATTR_WEBAUTHN['external_id'],
                        value=TEST_EXTERNAL_ID.encode('utf8'),
                    ),
                ),
                wct.insert().values(uid=TEST_UID, credential_id=TEST_EXTERNAL_ID.encode('utf8')),
            ],
        )

    def test_add_several_creds(self):
        cred = WebauthnCredential(id=1, external_id=TEST_EXTERNAL_ID)
        cred2 = WebauthnCredential(id=2, external_id=TEST_EXTERNAL_ID + '2')
        self.acc.webauthn_credentials.add(cred)
        self.acc.webauthn_credentials.add(cred2)

        eq_eav_queries(
            self.create(self.acc.webauthn_credentials),
            [
                eat_insert_odk().values(
                    self.eat_entry(
                        entity_id=TEST_ENTITY_ID,
                        type=EXT_ATTR_WEBAUTHN['external_id'],
                        value=TEST_EXTERNAL_ID.encode('utf8'),
                    ),
                ),
                wct.insert().values(uid=TEST_UID, credential_id=TEST_EXTERNAL_ID.encode('utf8')),
                eat_insert_odk().values(
                    self.eat_entry(
                        entity_id=TEST_ENTITY_ID + 1,
                        type=EXT_ATTR_WEBAUTHN['external_id'],
                        value=TEST_EXTERNAL_ID.encode('utf8') + b'2',
                    ),
                ),
                wct.insert().values(uid=TEST_UID, credential_id=TEST_EXTERNAL_ID.encode('utf8') + b'2'),
            ],
            any_order=True
        )

    def test_delete_everything(self):
        cred = WebauthnCredential(id=1, external_id=TEST_EXTERNAL_ID)
        cred2 = WebauthnCredential(id=2, external_id=TEST_EXTERNAL_ID + '2')
        self.acc.webauthn_credentials.add(cred)
        self.acc.webauthn_credentials.add(cred2)

        eq_eav_queries(
            self.delete(self.acc.webauthn_credentials),
            [
                wct.delete().where(wct.c.uid == TEST_UID),
                eat.delete().where(
                    and_(
                        eat.c.uid == TEST_UID,
                        eat.c.entity_type == EXTENDED_ATTRIBUTES_WEBAUTHN_TYPE,
                    ),
                ),
            ],
        )

    def test_nothing_to_do(self):
        eq_eav_queries(
            self.serialize(None, None),
            [],
        )
