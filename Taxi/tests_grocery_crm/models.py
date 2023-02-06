import copy
import json

from tests_grocery_crm import common
from tests_grocery_crm import headers

SELECT_INFORMER = """
SELECT informer_info
FROM crm.informers
WHERE id = %s
"""

INSERT_INFORMER = """
INSERT INTO crm.informers (
    id,
    informer_info
)
VALUES (%s, %s)
"""

SELECT_INFORMER_SHOWN_COUNT = """
SELECT shown_count
FROM crm.user_informers
WHERE informer_id = %s AND yandex_uid = %s
"""

INSERT_USER_INFORMER = """
INSERT INTO crm.user_informers (
    informer_id,
    yandex_uid,
    shown_count,
    idempotency_key
)
VALUES (%s, %s, %s, %s)
"""

SELECT_USER_INFORMER = """
SELECT informer_id, yandex_uid, shown_count, idempotency_key
FROM crm.user_informers
WHERE informer_id = %s AND yandex_uid = %s
"""


class Informer:
    def __init__(
            self,
            pgsql,
            informer_id,
            text=common.TEXT,
            picture=common.PICTURE,
            text_color=common.TEXT_COLOR,
            background_color=common.BACKGROUND_COLOR,
            modal=copy.deepcopy(common.MODAL),
            extra_data=copy.deepcopy(common.EXTRA_DATA),
            show_in_root=None,
            category_ids=None,
            category_group_ids=None,
            product_ids=None,
            stories=None,
            hide_if_product_is_missing=None,
            source=None,
            save_in_db=True,
    ):
        self.informer_id = informer_id
        self.text = text
        self.picture = picture
        self.text_color = text_color
        self.background_color = background_color
        self.modal = modal
        self.extra_data = extra_data
        self.show_in_root = show_in_root
        self.category_ids = category_ids
        self.category_group_ids = category_group_ids
        self.product_ids = product_ids
        self.stories = stories
        self.hide_if_product_is_missing = hide_if_product_is_missing

        self.source = source
        self.pg_db = pgsql['grocery_crm']
        if save_in_db:
            self.update_db()

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_INFORMER, [self.informer_id, json.dumps(self.json())],
        )

    def json(self):
        result = {}
        if self.text is not None:
            result['text'] = self.text
        if self.picture is not None:
            result['picture'] = self.picture
        if self.text_color is not None:
            result['text_color'] = self.text_color
        if self.background_color is not None:
            result['background_color'] = self.background_color
        if self.modal is not None:
            result['modal'] = self.modal
        if self.extra_data is not None:
            result['extra_data'] = self.extra_data
        if self.show_in_root is not None:
            result['catalog_extra_data'] = {}
            result['catalog_extra_data']['show_in_root'] = self.show_in_root
            if self.category_ids is not None:
                result['catalog_extra_data'][
                    'category_ids'
                ] = self.category_ids
            if self.category_group_ids is not None:
                result['catalog_extra_data'][
                    'category_group_ids'
                ] = self.category_group_ids
            if self.product_ids is not None:
                result['catalog_extra_data']['product_ids'] = self.product_ids
            if self.stories is not None:
                result['catalog_extra_data']['stories'] = self.stories
            if self.hide_if_product_is_missing is not None:
                result['catalog_extra_data'][
                    'hide_if_product_is_missing'
                ] = self.hide_if_product_is_missing
        return result

    def compare_with_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_INFORMER, [self.informer_id])
        result = cursor.fetchone()
        assert result
        assert self.json() == result[0]


class UserInformer:
    def __init__(
            self,
            pgsql,
            informer_id,
            yandex_uid=headers.YANDEX_UID,
            shown_count=1,
            idempotency_key='idempotency_key',
            save_in_db=True,
    ):
        self.informer_id = informer_id
        self.yandex_uid = yandex_uid
        self.shown_count = shown_count
        self.idempotency_key = idempotency_key

        self.pg_db = pgsql['grocery_crm']
        if save_in_db:
            self.update_db()

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_USER_INFORMER,
            [
                self.informer_id,
                self.yandex_uid,
                self.shown_count,
                self.idempotency_key,
            ],
        )

    def compare_with_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            SELECT_USER_INFORMER, [self.informer_id, self.yandex_uid],
        )
        result = cursor.fetchone()
        assert result == (
            self.informer_id,
            self.yandex_uid,
            self.shown_count,
            self.idempotency_key,
        )
