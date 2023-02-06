import dataclasses
import datetime
from typing import List
from typing import Optional
from typing import Union

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks.models import cart
# pylint: enable=import-error

from tests_grocery_marketing import common

# pylint: disable=invalid-name
GroceryCartItem = cart.GroceryCartItem
GroceryCartSubItem = cart.GroceryCartSubItem
GroceryCartItemV2 = cart.GroceryCartItemV2
# pylint: enable=invalid-name

UPSERT_COMING_SOON_SUBSCRIPTION_SQL = """
INSERT INTO grocery_marketing.coming_soon_subscriptions (
    lat,
    lon,
    location,
    region_id,
    subscribe,
    notified,
    processed,
    session,
    yandex_uid,
    raw_auth_context
)
VALUES (
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
;
"""

UPSERT_TAG_STAT_SQL = """
INSERT INTO grocery_marketing.tag_statistics (
    yandex_uid,
    tag,
    usage_count,
    last_order_ids,
    updated)
VALUES (
%s, %s, %s, %s, %s)
ON CONFLICT(yandex_uid, tag)
DO UPDATE SET
    yandex_uid = EXCLUDED.yandex_uid,
    tag = EXCLUDED.tag,
    usage_count = EXCLUDED.usage_count,
    last_order_ids = EXCLUDED.last_order_ids,
    updated = EXCLUDED.updated
;
"""

UPSERT_OTHER_TAG_STAT_SQL = """
INSERT INTO grocery_marketing.other_tag_statistics (
    id,
    id_type,
    tag,
    usage_count,
    last_order_ids,
    updated)
VALUES (
%s, %s, %s, %s, %s, %s)
ON CONFLICT(id, id_type, tag)
DO UPDATE SET
    id = EXCLUDED.id,
    id_type = EXCLUDED.id_type,
    tag = EXCLUDED.tag,
    usage_count = EXCLUDED.usage_count,
    last_order_ids = EXCLUDED.last_order_ids,
    updated = EXCLUDED.updated
;
"""

UPSERT_COMING_SOON_SUBSCRIPTION_SQL = """
UPDATE grocery_marketing.coming_soon_subscriptions SET
    created = %s
WHERE
    lat = %s AND lon = %s AND session = %s
;
"""

SELECT_COMING_SOON_SUBSCRIPTION_SQL = """
SELECT
    lat,
    lon,
    location,
    processed_depot_id,
    processed_item_id,
    region_id,
    subscribe,
    personal_phone_id,
    notified,
    processed,
    session,
    yandex_uid,
    raw_auth_context,
    created,
    updated,
    depot_id_subscribed
FROM grocery_marketing.coming_soon_subscriptions
WHERE session = %s and lat = %s and lon = %s
;
"""

SELECT_TAG_STAT_SQL = """
SELECT
    yandex_uid,
    tag,
    usage_count,
    last_order_ids,
    created,
    updated
FROM grocery_marketing.tag_statistics
WHERE yandex_uid = %s and tag = %s;
"""

SELECT_OTHER_TAG_STAT_SQL = """
SELECT
    id,
    id_type,
    tag,
    usage_count,
    last_order_ids,
    created,
    updated
FROM grocery_marketing.other_tag_statistics
WHERE id = %s and id_type = %s and tag = %s;
"""

SELECT_ALL_TAG_STAT_SQL = """
SELECT
    yandex_uid,
    tag,
    usage_count,
    last_order_ids,
    created,
    updated
FROM grocery_marketing.tag_statistics
"""

SELECT_ALL_OTHER_TAG_STAT_SQL = """
SELECT
    id,
    id_type,
    tag,
    usage_count,
    last_order_ids,
    created,
    updated
FROM grocery_marketing.other_tag_statistics
"""

REMOVE_TAG_STAT_SQL = """
DELETE FROM grocery_marketing.tag_statistics WHERE
yandex_uid = %s and tag = %s
;
"""

REMOVE_OTHER_TAG_STAT_SQL = """
DELETE FROM grocery_marketing.other_tag_statistics WHERE
id = %s and id_type = %s and tag = %s
;
"""

REMOVE_COMING_SOON_SUBSCRIPTION_SQL = """
DELETE FROM grocery_marketing.coming_soon_subscriptions WHERE
session = %s and lat = %s and lon = %s
;
"""


class TagStatistic:
    def __init__(
            self,
            pgsql,
            yandex_uid=None,
            tag=None,
            usage_count=None,
            last_order_ids=None,
            insert_in_pg=True,
            updated=None,
    ):
        self.pg_db = pgsql['grocery_marketing']
        if yandex_uid is None:
            yandex_uid = common.YANDEX_UID
        if tag is None:
            tag = 'some_tag'
        if usage_count is None:
            usage_count = 0
        if last_order_ids is None:
            last_order_ids = ['some_order_id']
        if updated is None:
            updated = datetime.datetime.now()

        self.yandex_uid = yandex_uid
        self.tag = tag
        self.usage_count = usage_count
        self.last_order_ids = last_order_ids
        self.created = None
        self.updated = updated
        if insert_in_pg:
            self._update_db()

    def _update_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(
            UPSERT_TAG_STAT_SQL,
            [
                self.yandex_uid,
                self.tag,
                self.usage_count,
                self.last_order_ids,
                self.updated,
            ],
        )

    def upsert(
            self,
            *,
            yandex_uid=None,
            tag=None,
            usage_count=None,
            last_order_ids=None,
    ):
        if yandex_uid is not None:
            self.yandex_uid = yandex_uid
        if tag is not None:
            self.tag = tag
        if usage_count is not None:
            self.usage_count = usage_count
        if last_order_ids is not None:
            self.last_order_ids = last_order_ids
        self._update_db()

    def update(self):
        cursor = self.pg_db.cursor()

        cursor.execute(SELECT_TAG_STAT_SQL, [self.yandex_uid, self.tag])
        result = cursor.fetchone()

        assert result
        (
            yandex_uid,
            tag,
            usage_count,
            last_order_ids,
            created,
            updated,
        ) = result

        self.yandex_uid = yandex_uid
        self.tag = tag
        self.usage_count = usage_count
        self.last_order_ids = last_order_ids
        self.created = created
        self.updated = updated

    @classmethod
    def fetch(cls, pgsql, yandex_uid, tag):
        result = TagStatistic(
            pgsql=pgsql, yandex_uid=yandex_uid, tag=tag, insert_in_pg=False,
        )

        result.update()
        return result

    def remove(self):
        cursor = self.pg_db.cursor()
        cursor.execute(REMOVE_TAG_STAT_SQL, [self.yandex_uid, self.tag])

    @classmethod
    def check_no(cls, pgsql, yandex_uid, tag):
        cursor = pgsql['grocery_marketing'].cursor()
        cursor.execute(SELECT_TAG_STAT_SQL, [yandex_uid, tag])

        result = cursor.fetchone()
        assert result is None


class OtherTagStatistic:
    def __init__(
            self,
            pgsql,
            user_id=None,
            id_type=None,
            tag=None,
            usage_count=None,
            last_order_ids=None,
            insert_in_pg=True,
            updated=None,
    ):
        self.pg_db = pgsql['grocery_marketing']
        if user_id is None:
            user_id = common.APPMETRICA_DEVICE_ID
        if id_type is None:
            id_type = 'appmetrica_device_id'
        if tag is None:
            tag = 'some_tag'
        if usage_count is None:
            usage_count = 0
        if last_order_ids is None:
            last_order_ids = ['some_order_id']
        if updated is None:
            updated = datetime.datetime.now()

        self.user_id = user_id
        self.id_type = id_type
        self.tag = tag
        self.usage_count = usage_count
        self.last_order_ids = last_order_ids
        self.created = None
        self.updated = updated
        if insert_in_pg:
            self._update_db()

    def _update_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(
            UPSERT_OTHER_TAG_STAT_SQL,
            [
                self.user_id,
                self.id_type,
                self.tag,
                self.usage_count,
                self.last_order_ids,
                self.updated,
            ],
        )

    def upsert(
            self,
            *,
            user_id=None,
            id_type=None,
            tag=None,
            usage_count=None,
            last_order_ids=None,
    ):
        if user_id is not None:
            self.user_id = user_id
        if id_type is not None:
            self.id_type = id_type
        if tag is not None:
            self.tag = tag
        if usage_count is not None:
            self.usage_count = usage_count
        if last_order_ids is not None:
            self.last_order_ids = last_order_ids
        self._update_db()

    def update(self):
        cursor = self.pg_db.cursor()

        cursor.execute(
            SELECT_OTHER_TAG_STAT_SQL, [self.user_id, self.id_type, self.tag],
        )
        result = cursor.fetchone()

        assert result
        (
            user_id,
            id_type,
            tag,
            usage_count,
            last_order_ids,
            created,
            updated,
        ) = result

        self.user_id = user_id
        self.id_type = id_type
        self.tag = tag
        self.usage_count = usage_count
        self.last_order_ids = last_order_ids
        self.created = created
        self.updated = updated

    @classmethod
    def fetch(cls, pgsql, user_id, id_type, tag):
        result = OtherTagStatistic(
            pgsql=pgsql,
            user_id=user_id,
            id_type=id_type,
            tag=tag,
            insert_in_pg=False,
        )

        result.update()
        return result

    def remove(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            REMOVE_OTHER_TAG_STAT_SQL, [self.user_id, self.id_type, self.tag],
        )

    @classmethod
    def check_no(cls, pgsql, user_id, id_type, tag):
        cursor = pgsql['grocery_marketing'].cursor()
        cursor.execute(SELECT_OTHER_TAG_STAT_SQL, [user_id, id_type, tag])

        result = cursor.fetchone()
        assert result is None


class ComingSoonSubscription:
    def __init__(
            self, pgsql, session=None, lat=None, lon=None, insert_in_pg=True,
    ):
        self.pg_db = pgsql['grocery_marketing']

        self.lat = lat
        self.lon = lon
        self.location = None
        self.processed_depot_id = None
        self.processed_item_id = None
        self.region_id = None
        self.subscribe = None
        self.personal_phone_id = None
        self.notified = None
        self.processed = None
        self.session = session
        self.yandex_uid = None
        self.raw_auth_context = None
        self.depot_id_subscribed = None

        self.created = None
        self.updated = None

    def _update_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(
            UPSERT_COMING_SOON_SUBSCRIPTION_SQL,
            [self.created, self.lat, self.lon, self.session],
        )

    def update(self):
        cursor = self.pg_db.cursor()

        cursor.execute(
            SELECT_COMING_SOON_SUBSCRIPTION_SQL,
            [self.session, self.lat, self.lon],
        )
        result = cursor.fetchone()

        assert result
        (
            lat,
            lon,
            location,
            processed_depot_id,
            processed_item_id,
            region_id,
            subscribe,
            personal_phone_id,
            notified,
            processed,
            session,
            yandex_uid,
            raw_auth_context,
            created,
            updated,
            depot_id_subscribed,
        ) = result

        self.yandex_uid = yandex_uid
        self.lat = lat
        self.lon = lon
        self.location = location
        self.processed_depot_id = processed_depot_id
        self.processed_item_id = processed_item_id
        self.region_id = region_id
        self.subscribe = subscribe
        self.personal_phone_id = personal_phone_id
        self.notified = notified
        self.processed = processed
        self.session = session
        self.yandex_uid = yandex_uid
        self.raw_auth_context = raw_auth_context
        self.depot_id_subscribed = depot_id_subscribed

        self.created = created
        self.updated = updated

    @classmethod
    def fetch(cls, pgsql, session, lat, lon):
        result = ComingSoonSubscription(
            pgsql=pgsql, session=session, lat=lat, lon=lon, insert_in_pg=False,
        )

        result.update()
        return result

    def upsert(self, *, created=None):
        if created is not None:
            self.created = created
        self._update_db()

    def remove(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            REMOVE_COMING_SOON_SUBSCRIPTION_SQL,
            [self.session, self.lat, self.lon],
        )


@dataclasses.dataclass
class MatchCondition:
    condition_name: str
    values: Union[List[str], str] = 'Any'
    exclusions: Optional[Union[List[str], str]] = None

    def as_object(self):
        if self.exclusions is not None:
            return {
                'condition_name': self.condition_name,
                'values': self.values,
                'exclusions': self.exclusions,
            }

        return {'condition_name': self.condition_name, 'values': self.values}
