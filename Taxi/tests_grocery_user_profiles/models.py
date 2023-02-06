import dataclasses
import datetime
import json

DEFAULT_CREATED = datetime.datetime(
    year=2020, month=3, day=10, tzinfo=datetime.timezone.utc,
)

UTC_TZ = datetime.timezone.utc
NOW = '2020-03-13T07:19:00+00:00'
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)
BEFORE_NOW = '2020-03-13T07:18:00+00:00'
BEFORE_NOW_DT = datetime.datetime(2020, 3, 13, 7, 18, 00, tzinfo=UTC_TZ)


INSERT_ANTIFRAUD_USER_PROFILE_SQL = """
INSERT INTO user_profiles.tags (
    created_at,
    updated_at,
    is_disabled,
    tag_name,
    tag_info,
    yandex_uid,
    personal_phone_id,
    appmetrica_device_id,
    bound_session
)
VALUES (
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
)
"""

SELECT_ANTIFRAUD_USER_PROFILE_SQL = """
SELECT
    created_at,
    updated_at,
    is_disabled,
    tag_name,
    tag_info,
    yandex_uid,
    personal_phone_id,
    appmetrica_device_id,
    bound_session
FROM user_profiles.tags
WHERE yandex_uid = %s
or personal_phone_id = %s
"""


@dataclasses.dataclass
class UserProfile:
    def __init__(
            self,
            pgsql,
            created_at,
            updated_at,
            is_disabled,
            tag_name,
            tag_info,
            yandex_uid,
            personal_phone_id,
            appmetrica_device_id,
            bound_session,
            write_in_db=True,
    ):
        self.pg_sql = pgsql['grocery_user_profiles']
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_disabled = is_disabled
        self.tag_name = tag_name
        self.tag_info = tag_info
        self.yandex_uid = yandex_uid
        self.personal_phone_id = personal_phone_id
        self.appmetrica_device_id = appmetrica_device_id
        self.bound_session = bound_session
        if write_in_db:
            self.update_db()

    def update_db(self):
        cursor = self.pg_sql.cursor()
        cursor.execute(
            INSERT_ANTIFRAUD_USER_PROFILE_SQL,
            [
                self.created_at,
                self.updated_at,
                self.is_disabled,
                self.tag_name,
                self.tag_info,
                self.yandex_uid,
                self.personal_phone_id,
                self.appmetrica_device_id,
                self.bound_session,
            ],
        )

    def compare_with_db(self):
        cursor = self.pg_sql.cursor()

        cursor.execute(
            SELECT_ANTIFRAUD_USER_PROFILE_SQL,
            [self.yandex_uid, self.personal_phone_id],
        )
        result = cursor.fetchone()
        assert result
        (
            _,  # created_at
            _,  # updated_at
            is_disabled,
            tag_name,
            tag_info,
            yandex_uid,
            personal_phone_id,
            appmetrica_device_id,
            bound_session,
        ) = result

        assert self.is_disabled == is_disabled
        assert self.tag_name == tag_name
        assert self.tag_info == json.dumps(tag_info)
        assert self.yandex_uid == yandex_uid
        assert self.personal_phone_id == personal_phone_id
        assert self.appmetrica_device_id == appmetrica_device_id
        assert self.bound_session == bound_session
