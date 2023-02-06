# -*- coding: utf-8 -*-

from passport.backend.core.db.utils import insert_with_on_duplicate_key_update
from passport.backend.social.common.db.schemas import (
    person_table,
    profile_table,
    refresh_token_table,
    token_table,
)
from passport.backend.social.common.token.db import TokenRecord
from sqlalchemy import sql


class SelectProfileByUseridDataQuery(object):
    def __init__(self, provider_id, userid, uid):
        self.params = {
            'provider_id': provider_id,
            'userid': userid,
            'uid': uid,
        }

    def to_sql(self):
        prt = profile_table
        return (
            prt.select()
            .where(
                sql.and_(
                    prt.c.provider_id == self.params['provider_id'],
                    prt.c.userid == self.params['userid'],
                    prt.c.uid == self.params['uid'],
                ),
            )
        )


class SelectProfileByProfileIdDataQuery(object):
    def __init__(self, profile_id):
        self.params = {
            'profile_id': profile_id,
        }

    def to_sql(self):
        prt = profile_table
        return prt.select().where(prt.c.profile_id == self.params['profile_id'])


class SelectTokensForProfileDataQuery(object):
    def __init__(self, profile_id):
        self.params = {'profile_id': profile_id}

    def to_sql(self):
        tt = token_table
        return (
            tt.select()
            .where(tt.c.profile_id == self.params['profile_id'])
            .order_by(sql.desc(tt.c.token_id))
            .limit(100)
        )


class SelectTokenByTokenIdDataQuery(object):
    def __init__(self, token_id):
        self.params = {'token_id': token_id}

    def to_sql(self):
        tt = token_table
        return tt.select().where(tt.c.token_id == self.params['token_id'])


class SelectRefreshTokensByTokenIdsDataQuery(object):
    def __init__(self, token_ids):
        self.params = {'token_ids': token_ids}

    def to_sql(self):
        rtt = refresh_token_table
        tt = token_table
        return (
            rtt.join(tt, tt.c.token_id == rtt.c.token_id).select(use_labels=True)
            .where(rtt.c.token_id.in_(self.params['token_ids']))
        )


class SelectRefreshTokenByTokenIdDataQuery(SelectRefreshTokensByTokenIdsDataQuery):
    def __init__(self, token_id):
        super(SelectRefreshTokenByTokenIdDataQuery, self).__init__([token_id])


class SelectTokenByValueForAccountDataQuery(object):
    def __init__(self, uid, application_id, value):
        self.params = {
            'uid': uid,
            'application_id': application_id,
            'value_hash': TokenRecord.eval_value_hash(value),
        }

    def to_sql(self):
        tt = token_table
        return (
            tt.select()
            .where(
                sql.and_(
                    tt.c.uid == self.params['uid'],
                    tt.c.application_id == self.params['application_id'],
                    tt.c.value_hash == self.params['value_hash'],
                ),
            )
        )


class InsertOrUpdateDataQuery(object):
    ON_DUPLICATE_UPDATE_KEYS = []
    TABLE = None
    VALUES = []
    DEFAULTS = {}

    def __init__(self, **kwargs):
        self.params = {}
        defaults = self.get_constructor_defaults()
        for name in self.VALUES:
            if name in kwargs:
                value = kwargs[name]
            elif name in defaults:
                value = defaults[name]
            else:
                raise TypeError('Required argument %s not found' % name)
            self.params[name] = value

    def to_sql(self):
        return (
            insert_with_on_duplicate_key_update(
                self.get_table(),
                self.get_on_duplicate_update_keys(),
            )
            .values(**self.get_values_dict())
        )

    def get_table(self):
        return self.TABLE

    def get_on_duplicate_update_keys(self):
        return self.ON_DUPLICATE_UPDATE_KEYS

    def get_values_dict(self):
        return {n: self.params[n] for n in self.VALUES}

    def get_constructor_defaults(self):
        retval = {}
        for key, value in self.DEFAULTS.iteritems():
            if callable(value):
                value = value()
            retval[key] = value
        return retval


def insert_or_update_to_update_data_query(cls):
    class UpdateDataQuery(cls):
        def __init__(self, **kwargs):
            self.VALUES = self.ON_DUPLICATE_UPDATE_KEYS

            super(UpdateDataQuery, self).__init__(**kwargs)

            pk_col = self.get_pk_column()
            if pk_col.name not in kwargs:
                raise TypeError('Required argument "%s" not found' % pk_col.name)
            self.params[pk_col.name] = kwargs[pk_col.name]

        def to_sql(self):
            return (
                self.get_table().update()
                .values(**self.get_values_dict())
                .where(self.get_pk_column() == self.get_pk_value())
            )

        def get_pk_column(self):
            pk_cols = self.get_table().primary_key.columns
            assert len(pk_cols) == 1
            return next(iter(pk_cols))

        def get_pk_value(self):
            pk_col = self.get_pk_column()
            return self.params[pk_col.name]
    return UpdateDataQuery


class InsertOrUpdateProfileDataQuery(InsertOrUpdateDataQuery):
    TABLE = profile_table
    VALUES = [
        'uid',
        'provider_id',
        'userid',
        'username',
        'allow_auth',
        'created',
        'verified',
        'confirmed',
        'referer',
        'yandexuid',
    ]
    ON_DUPLICATE_UPDATE_KEYS = [
        'username',
        'allow_auth',
        'referer',
        'yandexuid',
        'confirmed',
        'verified',
    ]
    DEFAULTS = dict(allow_auth=0)


UpdateProfileDataQuery = insert_or_update_to_update_data_query(InsertOrUpdateProfileDataQuery)


class InsertOrUpdateTokenDataQuery(InsertOrUpdateDataQuery):
    TABLE = token_table
    VALUES = [
        'uid',
        'profile_id',
        'application_id',
        'value',
        'value_hash',
        'secret',
        'scope',
        'expired',
        'created',
        'verified',
        'confirmed',
    ]
    ON_DUPLICATE_UPDATE_KEYS = [
        'value',
        'value_hash',
        'secret',
        'scope',
        'expired',
        'profile_id',
        'verified',
        'confirmed',
        'created',
    ]
    DEFAULTS = dict(
        value_hash='',
        secret='',
        expired='0000-00-00 00:00:00',
    )

    def __init__(self, **kwargs):
        super(InsertOrUpdateTokenDataQuery, self).__init__(**kwargs)

        if 'value_hash' not in kwargs:
            self.params['value_hash'] = TokenRecord.eval_value_hash(self.params['value'])


UpdateTokenDataQuery = insert_or_update_to_update_data_query(InsertOrUpdateTokenDataQuery)


class InsertOrUpdatePersonDataQuery(InsertOrUpdateDataQuery):
    TABLE = person_table
    VALUES = [
        'profile_id',
        'firstname',
        'lastname',
        'nickname',
        'email',
        'phone',
        'country',
        'city',
        'birthday',
        'gender',
    ]
    ON_DUPLICATE_UPDATE_KEYS = [
        'firstname',
        'lastname',
        'nickname',
        'email',
        'phone',
        'country',
        'city',
        'birthday',
        'gender',
    ]
    DEFAULTS = dict(
        firstname='',
        lastname='',
        nickname='',
        email='',
        phone='',
        country='',
        city='',
        birthday='0000-00-00',
        gender='',
    )


UpdatePersonDataQuery = insert_or_update_to_update_data_query(InsertOrUpdatePersonDataQuery)
