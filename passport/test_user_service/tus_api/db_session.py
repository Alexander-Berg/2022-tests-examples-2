# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import logging

from passport.backend.qa.test_user_service.tus_api.db import get_db
from passport.backend.qa.test_user_service.tus_api.db_schema import (
    consumer_test_accounts_table,
    tag_table,
    user_table,
    user_tags_table,
)
from passport.backend.qa.test_user_service.tus_api.exceptions import AccountNotFoundError
from passport.backend.qa.test_user_service.tus_api.models.account import Account


log = logging.getLogger(__name__)


class Session:

    def __init__(self, env):
        self.env = env

    def get_user_by_uid(self, uid):
        user_list = get_db().run_queries(get_db().get_user_by_uid(uid, self.env))[0]
        assert len(user_list) < 2, 'We have %d users with the same uid=%s. WTF?' % (len(user_list), uid)
        return Account(**user_list[0]) if len(user_list) == 1 else None

    def get_user_by_login(self, login):
        user_list = get_db().run_queries(get_db().get_user_by_login(login, self.env))[0]
        assert len(user_list) < 2, 'We have %d users with the same logins=%s. WTF?' % (len(user_list), login)
        return Account(**user_list[0]) if len(user_list) == 1 else None

    def get_uids_with_tags(self, consumer_name, client_login, offset):
        accounts_data = get_db().run_queries(get_db().get_uids_with_tags(consumer_name, client_login, offset, self.env))[0]
        return [str(account[0]) for account in accounts_data]

    def get_user_for_client_by_uid(self, consumer_name, uid, client_login):
        user_list = get_db().run_queries(get_db().get_account_with_uid(consumer_name, uid, client_login, self.env))[0]
        assert len(user_list) < 2, 'We have %d users with the same uid=%s. WTF?' % (len(user_list), uid)
        return Account(**user_list[0]) if len(user_list) == 1 else None

    def get_user_for_client_by_login(self, consumer_name, login, client_login):
        user_list = get_db().run_queries(
            get_db().get_account_with_login(consumer_name, login, client_login, self.env)
        )[0]
        assert len(user_list) < 2, 'We have %d users with the same logins=%s. WTF?' % (len(user_list), login)
        return Account(**user_list[0]) if len(user_list) == 1 else None

    def get_user_for_client_with_tags(self, consumer_name, tags, ignore_locks, client_login):
        user_list = get_db().run_queries(
            get_db().get_accounts_with_tags(consumer_name, tags, ignore_locks, client_login, self.env)
        )[0]
        return [Account(**user) for user in user_list]

    def get_tus_consumers_by_uid(self, uid):
        """
        Возвращает консьмер, к которому привязан аккаунт.
        Если по какой-то причине такого консьюмера нет -> нет консьюмера - нет аккаунта
        :param uid: идентификатор тестового аккаунта
        :return: косньюмер, к которому привязан uid
        """
        tus_consumers = get_db().get(consumer_test_accounts_table, uid=uid, env=self.env)
        if len(tus_consumers) == 0:
            raise AccountNotFoundError('No suitable account in TUS DB')
        return tus_consumers

    def save_user_to_tus(self, uid, login, password, delete_at):
        return get_db().add(
            user_table,
            uid=uid,
            login=login,
            password=password,
            locked_until=datetime.now() - timedelta(seconds=1),
            delete_at=delete_at,
            env=self.env
        )

    def remove_user(self, uid):
        return get_db().remove(user_table, uid=uid, env=self.env)

    def update_account_lock(self, uid, new_lock_ts, ignore_current_lock):
        return get_db().run_queries(get_db().update_account_lock(uid, new_lock_ts, ignore_current_lock, self.env))[0]

    def is_tag_exists(self, tag):
        tags_list = get_db().get(tag_table, tag=tag)
        return len(tags_list) > 0

    def get_tag_id(self, tag):
        tags_list = get_db().get(tag_table, tag=tag)
        return tags_list[0]['tag_id'] if len(tags_list) == 1 else None

    def add_tag(self, tag):
        return get_db().add(tag_table, tag=tag)

    def add_tag_for_uid(self, uid, tag_id):
        return get_db().add(user_tags_table, uid=uid, tag_id=tag_id, env=self.env)

    def get_ids_for_existing_tags(self, tags):
        query_result = get_db().run_queries(get_db().get_tag_ids(tags))[0]
        return [x['tag_id'] for x in query_result]

    def get_user_with_uid_and_tag(self, uid, tag_id):
        return get_db().get(user_tags_table, uid=uid, tag_id=tag_id, env=self.env)

    def is_user_saved_to_tus(self, uid):
        is_user_saved = self.get_user_by_uid(uid)
        if is_user_saved:
            return True
        else:
            return False

    def get_saved_user(self, uid):
        user = self.get_user_by_uid(uid)
        if not user:
            raise AccountNotFoundError('No suitable account in TUS DB')
        return user

    def create_missing_tags(self, tags):
        for tag in tags:
            if not self.is_tag_exists(tag):
                self.add_tag(tag)

    def bind_tus_consumer_for_test_account(self, uid, tus_consumer):
        """
        К моменту вызова tus_consumer уже проверен на валидность (если консьюмера нет -> у пользователя нет доступа)
        uid аккаунта также
        """
        get_db().add(consumer_test_accounts_table, uid=uid, consumer_name=tus_consumer, env=self.env)

    def get_tags_list_for_uid(self, uid):
        return get_db().run_queries(get_db().get_tag_list_for_uid(uid, self.env))[0]

    def get_consumer_list_for_uid(self, uid):
        return get_db().run_queries(get_db().get_consumer_list_for_uid_query(uid, self.env))[0]
