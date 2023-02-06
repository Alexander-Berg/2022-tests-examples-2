# -*- coding: utf-8 -*-
from passport.backend.oauth.core.db.eav.attributes import (
    DatetimeAttribute,
    EncryptedStringAttribute,
    register_attribute_types,
)
from passport.backend.oauth.core.db.eav.index import Index
from passport.backend.oauth.core.db.eav.model import (
    EavAttr,
    EavModel,
)
from passport.backend.oauth.core.db.eav.schemas import (
    auto_id_columns,
    central_metadata,
    eav_columns,
    register_auto_id,
)
from passport.backend.oauth.core.db.schemas import (
    client_attributes_table,
    client_by_owner_table,
    client_by_params_table,
    client_by_uid_table,
    token_attributes_table,
    token_by_access_token_table,
    token_by_alias_table,
    token_by_params_table,
)
from sqlalchemy.schema import Table
from sqlalchemy.types import Integer


class TokenForTest(EavModel):
    """Пример шардированной 'модели', с которой будет работать код"""
    _entity_name = 'token'
    _table = token_attributes_table
    _indexes = {
        'params': Index(token_by_params_table),
        'access_token': Index(token_by_access_token_table),
        'alias': Index(token_by_alias_table, nullable_fields=['alias']),
    }

    access_token = EavAttr()
    uid = EavAttr()
    client_id = EavAttr()
    scope_ids = EavAttr()
    device_id = EavAttr()
    meta = EavAttr()
    alias = EavAttr()

    bad_attr = EavAttr('bad_attr')


class ClientForTest(EavModel):
    """Пример 'модели' из центральной БД, с которой будет работать код"""
    _entity_name = 'client'
    _table = client_attributes_table
    _indexes = {
        'uid': Index(client_by_uid_table),
        'params': Index(
            client_by_params_table,
            distinct_matched_key_fields=['uid', 'display_id', 'approval_status', 'is_yandex'],
            collection_fields=['services'],
        ),
        'owner': Index(
            client_by_owner_table,
            distinct_matched_key_fields=['owner_groups', 'owner_uids'],
            collection_fields=['uids'],
            nullable_fields=['owner_groups', 'owner_uids'],
            synthetic_fields=['uids'],
            extra_fields_generator=lambda values: {'uids': b'|fake_value|'},
        ),
    }

    uid = EavAttr()
    display_id = EavAttr()
    scope_ids = EavAttr()
    secret = EavAttr()
    is_blocked = EavAttr()
    is_yandex = EavAttr()
    approval_status = EavAttr()
    services = EavAttr()
    default_title = EavAttr()
    deleted = EavAttr()
    owner_groups = EavAttr()
    owner_uids = EavAttr()

    @property
    def is_deleted(self):
        return self.deleted


register_auto_id('tvm_secret_key', Table('auto_id_tvm_secret_key', central_metadata, *auto_id_columns()))
register_attribute_types(
    'tvm_secret_key',
    {
        1: EncryptedStringAttribute('public_secret'),
        2: EncryptedStringAttribute('private_secret'),
        3: DatetimeAttribute('created'),
        4: DatetimeAttribute('deleted'),
    },
)


class SecretKeyForTest(EavModel):
    """Пример 'модели' с шифруемыми полями"""
    _entity_name = 'tvm_secret_key'
    _table = Table('tvm_secret_key_attributes', central_metadata, *eav_columns(id_type=Integer))
    _indexes = {}

    public_secret = EavAttr()
    private_secret = EavAttr()
