# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import logging

from passport.backend.qa.test_user_service.tus_api.db_session import Session
from passport.backend.qa.test_user_service.tus_api.exceptions import (
    SaveAccountFailedError,
    TusConsumerAccessDenied,
    TusConsumerNotMatchedError,
)
from passport.backend.qa.test_user_service.tus_api.fillers import normalize_login


log = logging.getLogger(__name__)


def get_account_by_uid(uid, env):
    return Session(env).get_user_by_uid(uid)


def get_account_by_login(login, env):
    return Session(env).get_user_by_login(login)


def get_uids_with_tags(consumer_name, client_login, offset, env):
    return Session(env).get_uids_with_tags(consumer_name, client_login, offset)


def get_account_for_client_by_uid(consumer_name, uid, client_login, env):
    return Session(env).get_user_for_client_by_uid(consumer_name, uid, client_login)


def get_account_for_client_by_login(consumer_name, login, client_login, env):
    return Session(env).get_user_for_client_by_login(consumer_name, login, client_login)


def get_account_for_client_with_tags(consumer_name, tags, ignore_locks, client_login, env):
    return Session(env).get_user_for_client_with_tags(consumer_name, tags, ignore_locks, client_login)


def get_saved_account(uid, env):
    return Session(env).get_saved_user(uid)


def _is_user_saved_with_consumer(uid, tus_consumer, session):
    consumer_as_tag = format_tus_consumer_to_tag(tus_consumer)
    tag_id = session.get_tag_id(consumer_as_tag)
    records = session.get_user_with_uid_and_tag(uid, tag_id)
    return len(records) == 1


def remove_user_from_tus_db(uid, tus_consumer, env):
    session = Session(env)
    account = session.get_saved_user(uid)
    if _is_user_saved_with_consumer(account.uid, tus_consumer, session):
        return session.remove_user(uid)
    else:
        raise TusConsumerNotMatchedError('User with uid {} belongs to a different tus_consumer'.format(account.uid))


def try_lock_account(account, duration, ignore_locks, env):
    return Session(env).update_account_lock(account.uid, datetime.now() + timedelta(seconds=duration), ignore_locks)


def unlock_account(uid, env):
    session = Session(env)
    account = session.get_saved_user(uid)
    return session.update_account_lock(account.uid, datetime.fromtimestamp(0), ignore_current_lock=True)


def format_tus_consumer_to_tag(tus_consumer):
    return 'tus_consumer_value=' + tus_consumer


def get_tags_for_uid(uid, env):
    """
    Формирует список тегов по uid
    :param uid: идентификатор тестового аккаунта
    :return: список полученных тегов по заданному uid
    """
    query_result = Session(env).get_tags_list_for_uid(uid)
    return [x['tag'] for x in query_result]


def get_consumer_list_by_uid(uid, env):
    """
    Формирует список консьюмеров (берутся из таблицы тегов) по uid
    :param uid: идентификатор тестового аккаунта
    :return: список полученных tus_consumer по заданному uid
    """
    query_result = Session(env).get_consumer_list_for_uid(uid)
    return [x['tag'] for x in query_result]


def get_tus_consumer_by_account_uid(uid, env):
    """
    Возвращаем tus_consumer, которому принадлежит тестовый аккаунт
    :param uid: идентификатор тестового аккаунта
    :return: tus_consumer
    """
    tus_consumer = Session(env).get_tus_consumers_by_uid(uid)[0]['consumer_name']
    return tus_consumer


def check_access_to_account(uid, client_consumer, env):
    """
    Проверяет, что у пользователя есть доступ к аккаунту
    :param uid: идентификатор аккаунта
    :param client_consumer: имя консьюмера, с которым сделал запрос клиент
    :raise TusConsumerAccessDenied: если консьюмеры клиента и аккаунта в TUS не совпадают
    """
    account_consumer = Session(env).get_tus_consumers_by_uid(uid)[0]['consumer_name']
    if client_consumer != account_consumer:
        raise TusConsumerAccessDenied(
            "Requested account belongs to '{account_consumer}' consumer. Requested consumer: '{consumer}'".format(
                account_consumer=account_consumer,
                consumer=client_consumer,
            )
        )


def _save_user_to_tus_db(uid, login, password, delete_at, session):
    login = normalize_login(login)
    if not session.is_user_saved_to_tus(uid):
        log.debug('Account {login} wasn`t saved in DB; env = {env}'.format(login=login, env=session.env))
        return session.save_user_to_tus(uid, login, password, delete_at)
    else:
        raise SaveAccountFailedError('User with uid {} already exists. You can /1/remove_account_from_tus/ and then '
                                     '/1/save_account/'.format(uid))


def _add_tags_for_user(uid, tags, session):
    session.create_missing_tags(tags)
    tags_ids = session.get_ids_for_existing_tags(tags)
    for tag_id in tags_ids:
        session.add_tag_for_uid(uid, tag_id)


def _add_tus_consumer_for_user(uid, tus_consumer, session):
    """
    Добавляет тег тестовому аккаунту и привязывает аккаунт к консьюмеру
    :param uid: uid тестового аккаунта
    :param tus_consumer: консьюмер
    """
    consumer_as_tag = format_tus_consumer_to_tag(tus_consumer)
    session.create_missing_tags([consumer_as_tag])
    tag_id = session.get_tag_id(consumer_as_tag)
    session.add_tag_for_uid(uid, tag_id)
    session.bind_tus_consumer_for_test_account(uid, tus_consumer)
    log.debug(
        'Bound account {uid} (env = {env}) to consumer {tus_consumer}'.format(
            uid=uid,
            env=session.env,
            tus_consumer={tus_consumer},
        )
    )


def save_account_to_db(uid, login, password, delete_at, tags, tus_consumer, env):
    session = Session(env)
    _save_user_to_tus_db(uid, login, password, delete_at, session)
    try:
        if len(tags) > 0:
            _add_tags_for_user(uid, tags, session)
        _add_tus_consumer_for_user(uid, tus_consumer, session)
        return True
    except Exception as e:
        log.critical(e)
        return False


def get_passport_environment_for_response(env):
    env = env.upper()
    if env == 'TEST':
        return 'testing'
    elif env == 'PROD':
        return 'production'
    elif env == 'TEAM':
        return 'team'
    elif env == 'TEAM_TEST':
        return 'team-test'
    elif env == 'EXTERNAL':
        return 'external'
    else:
        raise KeyError('Unknown environment')
