import tests_bank_notifications.db_helpers as db_helpers
import tests_bank_notifications.defaults as defaults
import tests_bank_notifications.models as models


def default_headers():
    headers = defaults.auth_headers()
    headers['X-YaBank-ColorTheme'] = defaults.SYSTEM_KEY
    return headers


def default_json(event_type=defaults.EVENT_TYPE, limit=200, cursor=None):
    res = {'event_type': event_type, 'limit': limit}
    if cursor is not None:
        res['cursor'] = cursor
    return res


def insert_events(
        pgsql,
        count=1,
        event_type=defaults.EVENT_TYPE,
        experiment=None,
        description=defaults.DESCRIPTION,
        defaults_group=defaults.DEFAULTS_GROUP,
        bank_uid=defaults.BUID,
        action=defaults.ACTION,
        title=defaults.TITLE,
        title_tanker_args=None,
        description_tanker_args=None,
        payload=None,
):
    res = []
    for _ in range(count):
        event = models.Event.default(
            bank_uid=bank_uid,
            event_id=defaults.gen_uuid(),
            event_type=event_type,
            defaults_group=defaults_group,
            description=description,
            experiment=experiment,
            action=action,
            title=title,
            title_tanker_args=title_tanker_args,
            description_tanker_args=description_tanker_args,
            payload=payload,
        )
        db_response = db_helpers.insert_event(pgsql, event)
        assert len(db_response) == 1
        res.append(event)
    return res


def insert_marks(pgsql, event_ids, buid=defaults.BUID):
    for event_id in event_ids:
        db_response = db_helpers.insert_mark(pgsql, buid, event_id)
        assert len(db_response) == 1


def check_failed_response(response, status_code, code, message=None):
    assert response.status_code == status_code
    resp_json = response.json()
    assert len(resp_json) == 2
    assert resp_json['code'] == code
    if message is not None:
        assert resp_json['message'] == message
    else:
        assert len(resp_json['message']) > 1
