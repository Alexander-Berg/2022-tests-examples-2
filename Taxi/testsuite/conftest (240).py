# pylint: disable=redefined-outer-name
import pytest

# root conftest for service eats-moderation
pytest_plugins = ['eats_moderation_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_moderation'].dict_cursor()

    return create_cursor


@pytest.fixture()
def insert_moderation_task(get_cursor):
    def do_insert_task(task_id, context_id, payload_id, tag=None):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_moderation.moderation_queue ( '
            'task_id,'
            'context_id,'
            'payload_id,'
            'tag'
            ') VALUES (%s, %s, %s, %s) '
            'RETURNING task_id',
            (task_id, context_id, payload_id, tag),
        )
        return cursor.fetchone()[0]

    return do_insert_task


@pytest.fixture()
def get_moderation_task(get_cursor):
    def do_get_task(task_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_moderation.moderation_queue '
            'WHERE task_id = %s',
            [task_id],
        )
        return cursor.fetchone()

    return do_get_task


@pytest.fixture()
def get_moderation_task_by_tag(get_cursor):
    def do_get_task_by_tag(tag):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_moderation.moderation_queue ' 'WHERE tag = %s',
            [tag],
        )
        return cursor.fetchall()

    return do_get_task_by_tag


@pytest.fixture()
def insert_moderator(get_cursor):
    def do_insert_moderator(value):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_moderation.moderators ( '
            'moderator_context'
            ') VALUES (%s) '
            'RETURNING moderator_id',
            [value],
        )
        return cursor.fetchone()[0]

    return do_insert_moderator


@pytest.fixture()
def get_moderator(get_cursor):
    def do_get_moderator(moderator_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_moderation.moderators WHERE moderator_id = %s',
            [moderator_id],
        )
        return cursor.fetchone()

    return do_get_moderator


@pytest.fixture()
def insert_moderation(get_cursor):
    def do_insert_moderation(
            ident,
            task_id,
            payload_id,
            status,
            reasons,
            moderator_id,
            tag=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_moderation.moderation ( '
            'id, '
            'task_id, '
            'payload_id, '
            'status, '
            'reasons, '
            'moderator_id, '
            'tag'
            ') VALUES (%s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id',
            (ident, task_id, payload_id, status, reasons, moderator_id, tag),
        )
        return cursor.fetchone()[0]

    return do_insert_moderation


@pytest.fixture()
def get_moderation(get_cursor):
    def do_get_moderation(task_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_moderation.moderation WHERE task_id = %s',
            [task_id],
        )
        return cursor.fetchall()

    return do_get_moderation


@pytest.fixture()
def insert_reason(get_cursor):
    def do_insert_reason(title, value):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_moderation.reasons ( '
            'title, '
            'value '
            ') VALUES (%s, %s) '
            'RETURNING reason_id',
            (title, value),
        )
        return cursor.fetchone()[0]

    return do_insert_reason


@pytest.fixture()
def insert_payload(get_cursor):
    def do_insert_payload(scope, queue, external_id, value):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_moderation.payloads ( '
            'scope, '
            'queue, '
            'external_id, '
            'value '
            ') VALUES (%s, %s, %s, %s) '
            'RETURNING payload_id',
            (scope, queue, external_id, value),
        )
        return cursor.fetchone()[0]

    return do_insert_payload


@pytest.fixture()
def remove_payload(get_cursor):
    def do_remove_payload(payload_id):
        cursor = get_cursor()
        cursor.execute(
            'DELETE FROM eats_moderation.payloads WHERE payload_id = %s',
            [payload_id],
        )

    return do_remove_payload


@pytest.fixture()
def get_payload(get_cursor):
    def do_get_payload(payload_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_moderation.payloads WHERE payload_id = %s',
            [payload_id],
        )
        return cursor.fetchone()

    return do_get_payload


@pytest.fixture()
def insert_context(get_cursor):
    def do_insert_context(value):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_moderation.contexts ( '
            'value '
            ') VALUES (%s) '
            'RETURNING context_id',
            [value],
        )
        return cursor.fetchone()[0]

    return do_insert_context


@pytest.fixture()
def get_context(get_cursor):
    def do_get_context(context_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_moderation.contexts WHERE context_id = %s',
            [context_id],
        )
        return cursor.fetchone()

    return do_get_context
