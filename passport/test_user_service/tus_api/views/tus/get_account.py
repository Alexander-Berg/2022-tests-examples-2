# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import logging
from math import ceil

from formencode import validators
from passport.backend.qa.test_user_service.tus_api.backend import (
    format_tus_consumer_to_tag,
    get_account_for_client_by_login,
    get_account_for_client_by_uid,
    get_account_for_client_with_tags,
    get_passport_environment_for_response,
    get_tags_for_uid,
    try_lock_account,
)
from passport.backend.qa.test_user_service.tus_api.common.blackbox.blackbox import get_userinfo_by_uid
from passport.backend.qa.test_user_service.tus_api.exceptions import (
    AccountNotFoundError,
    TusConsumerAccessDenied,
)
from passport.backend.qa.test_user_service.tus_api.fillers import normalize_login
from passport.backend.qa.test_user_service.tus_api.idm_backend import check_access_to_consumer
from passport.backend.qa.test_user_service.tus_api.settings import DEFAULT_TUS_CONSUMER
from passport.backend.qa.test_user_service.tus_api.validators import (
    EnvValidator,
    TagsValidator,
    TusConsumer,
    WeakLoginValidator,
    WeakUidValidator,
)
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.tus.tus_base import TusBaseView


log = logging.getLogger(__name__)


class GetAccountForm(Schema):
    uid = WeakUidValidator(if_missing=None)
    login = WeakLoginValidator(not_empty=True, if_missing=None, strip=True)
    tags = TagsValidator()
    tus_consumer = TusConsumer(not_empty=True, strip=True)
    ignore_locks = validators.StringBool(not_empty=True, if_missing=False, strip=True)
    lock_duration = validators.Int(not_empty=True, if_missing=0, strip=True, min=0, max=86400)
    with_userinfo = validators.StringBool(not_empty=True, if_missing=False, strip=True)
    with_saved_tags = validators.StringBool(not_empty=True, if_missing=False, strip=True)
    env = EnvValidator(not_empty=True, if_missing='TEST', strip=True)


class GetAccount(TusBaseView):
    form = GetAccountForm

    def __init__(self):
        super(GetAccount, self).__init__()
        self.account_uid = None

    @staticmethod
    def remove_locked(candidates):
        current_ts = datetime.now()
        for candidate in candidates:
            if candidate.locked_until and candidate.locked_until >= current_ts:
                candidates.remove(candidate)

    def get_suitable_accounts(self, ignore_locks):
        env = self.form_values['env']
        tus_consumer = self.form_values['tus_consumer']
        client_login = self.requester_info['login']
        if 'uid' in self.form_values:
            account = get_account_for_client_by_uid(tus_consumer, self.form_values['uid'], client_login, env)
            return [account] if account else []
        if 'login' in self.form_values:
            login = normalize_login(self.form_values['login'])
            account = get_account_for_client_by_login(tus_consumer, login, client_login, env)
            return [account] if account else []

        tags = self.form_values.get('tags', [])
        tags.append(format_tus_consumer_to_tag(tus_consumer))

        log.debug(tags)
        return get_account_for_client_with_tags(tus_consumer, tags, ignore_locks, client_login, env)

    def choose_suitable_account(self):
        ignore_locks = self.form_values['ignore_locks']
        lock_duration = self.form_values['lock_duration']

        candidates = self.get_suitable_accounts(ignore_locks=ignore_locks)

        if not ignore_locks:
            self.remove_locked(candidates)  # filter locked when we get account by uid or login

        account = None
        for candidate in candidates:
            if lock_duration:
                has_acquired_lock = try_lock_account(candidate, lock_duration, ignore_locks, self.form_values['env'])
                if has_acquired_lock:
                    account = candidate
                    account.locked_until = datetime.now() + timedelta(seconds=lock_duration)
                    break
            else:
                account = candidate
                break

        if not account:
            # Получаем список аккаунтов с ignore_locks=True, поскольку выше могли получить не все аккаунты
            accounts_with_lock = self.get_suitable_accounts(ignore_locks=True)
            has_accounts_but_all_are_locked = len(accounts_with_lock) > 0
            if has_accounts_but_all_are_locked:
                nearest_unlock_time = min(accounts_with_lock, key=lambda acc: acc.locked_until).locked_until
                seconds_to_unlock = (nearest_unlock_time - datetime.now()).total_seconds()
                time_to_unlock = int(ceil(seconds_to_unlock))
                self.response_values = {'time_to_unlock': time_to_unlock}
                raise AccountNotFoundError(
                    'All suitable accounts are locked. Nearest time to unlock is {time_to_unlock} seconds'.format(
                        time_to_unlock=time_to_unlock
                    )
                )
            raise AccountNotFoundError('No suitable account in TUS DB')
        return account

    def process_request(self):
        self.check_access()

        env = self.form_values['env']
        with_saved_tags = self.form_values['with_saved_tags']
        with_userinfo = self.form_values['with_userinfo']
        account = self.choose_suitable_account()
        delete_at = str(account.delete_at) if account.delete_at else None

        account_data = {
            'uid': str(account.uid),
            'login': account.login,
            'password': account.password,
            'locked_until': str(account.locked_until),
            'delete_at': delete_at,
        }
        # TODO: return login + normalized_login when /get_account/?with_userinfo=1

        if with_saved_tags:
            saved_tags = get_tags_for_uid(account.uid, env)
            account_data['tags'] = saved_tags

        response = {
            'status': 'ok',
            'account': account_data,
            'passport_environment': get_passport_environment_for_response(env)
        }

        if with_userinfo:
            userinfo = get_userinfo_by_uid(account.uid, self.client_ip, env)
            response['userinfo'] = userinfo

        self.response_values = response

    def check_access(self):
        tus_consumer = self.form_values['tus_consumer']
        if tus_consumer == DEFAULT_TUS_CONSUMER:
            raise TusConsumerAccessDenied(
                'It is forbidden to call /1/get_account/ with common consumer\'{consumer}\'.'
                'To create new consumer use /1/create_tus_consumer/'.format(consumer=DEFAULT_TUS_CONSUMER)
            )

        # можно обойтись без этой проверки (так как она есть в запросе в БД на получение аккаунта),
        # но тогда при отсутствии доступа к консьюмеру будет ошибка account.not_found
        check_access_to_consumer(self.requester_info['login'], tus_consumer)

        self.yasm_logger.log(
            client_login=self.requester_info['login'],
            tus_consumer=tus_consumer,
        )


__all__ = (
    'GetAccount',
)
