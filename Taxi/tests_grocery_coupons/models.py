import datetime

from tests_grocery_coupons import consts

UTC_TZ = datetime.timezone.utc
NOW = '2022-01-01T10:00:00+00:00'
NOW_DT = datetime.datetime(2022, 1, 1, 10, 00, 00, tzinfo=UTC_TZ)

SELECT_ERROR_LOG_SQL = """
SELECT
    created,
    coupon,
    error_code,
    cart_id,
    yandex_uid,
    personal_phone_id,
    coupon_type
FROM coupons.errors_log
WHERE coupon = %s AND error_code = %s AND cart_id = %s
"""

SELECT_ERROR_LOG_BY_COUPON = """
SELECT COUNT(*)
FROM coupons.errors_log
WHERE coupon = %s AND cart_id = %s
"""

SELECT_USER_COUPONS = """
SELECT coupon, yandex_uid, personal_phone_id FROM coupons.user_coupons
WHERE yandex_uid = %s
"""

SAVE_USER_COUPON = """
INSERT INTO coupons.user_coupons
VALUES (%s, %s, %s)
ON CONFLICT DO NOTHING
"""


class ErrorLog:
    def __init__(
            self,
            pgsql,
            created=NOW_DT,
            coupon='test_coupon',
            error_code='test_error_code',
            cart_id=consts.CART_ID,
            yandex_uid=consts.YANDEX_UID,
            personal_phone_id=consts.PERSONAL_PHONE_ID,
            coupon_type='support',
    ):
        self.pg_db = pgsql['grocery_coupons']
        self.created = created
        self.coupon = coupon
        self.error_code = error_code
        self.cart_id = cart_id
        self.yandex_uid = yandex_uid
        self.personal_phone_id = personal_phone_id
        self.coupon_type = coupon_type

    def check_no_log(self):
        cursor = self.pg_db.cursor()

        cursor.execute(SELECT_ERROR_LOG_BY_COUPON, [self.coupon, self.cart_id])
        result = cursor.fetchone()[0]
        assert result == 0

    def compare_with_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(
            SELECT_ERROR_LOG_SQL, [self.coupon, self.error_code, self.cart_id],
        )
        result = cursor.fetchone()
        assert result
        (
            # created is pain to properly compare
            _,
            coupon,
            error_code,
            cart_id,
            yandex_uid,
            personal_phone_id,
            coupon_type,
        ) = result

        assert self.coupon == coupon
        assert self.error_code == error_code
        assert self.cart_id == cart_id
        assert self.yandex_uid == yandex_uid
        assert self.personal_phone_id == personal_phone_id
        assert self.coupon_type == coupon_type


class UserCoupon:
    def __init__(self, pgsql, coupon, yandex_uid, personal_phone_id):
        self.pg_db = pgsql['grocery_coupons']
        self.coupon = coupon
        self.yandex_uid = yandex_uid
        self.personal_phone_id = personal_phone_id

    def save(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            SAVE_USER_COUPON,
            [self.coupon, self.yandex_uid, self.personal_phone_id],
        )


def get_user_coupons(pgsql, yandex_uid):
    pg_db = pgsql['grocery_coupons']
    cursor = pg_db.cursor()
    cursor.execute(SELECT_USER_COUPONS, [yandex_uid])
    result = cursor.fetchall()
    coupons = []
    for row in result:
        coupons.append(
            UserCoupon(
                pgsql,
                coupon=row[0],
                yandex_uid=row[1],
                personal_phone_id=row[2],
            ),
        )
    return coupons
