# pylint: disable=too-many-lines
import csv
import dataclasses
import datetime
import json
import uuid

DEFAULT_CREATED = datetime.datetime(
    year=2020, month=3, day=10, tzinfo=datetime.timezone.utc,
)

UTC_TZ = datetime.timezone.utc
NOW = '2020-03-13T07:19:00+00:00'
NOW_DT = datetime.datetime(2020, 3, 13, 7, 19, 00, tzinfo=UTC_TZ)

ONE_MINUTE_FROM_NOW = '2020-03-13T07:20:00+00:00'
THREE_MINUTES_FROM_NOW = '2020-03-13T07:22:00+00:00'
SIX_MINUTES_FROM_NOW = '2020-03-13T07:25:00+00:00'

HALF_A_DAY_BEFORE_NOW = '2020-03-13T19:19:00+00:00'
ONE_AND_A_HALF_DAYS_BEFORE_NOW = '2020-03-11T19:19:00+00:00'
THREE_DAYS_BEFORE_NOW = '2020-03-10T07:19:00+00:00'

NOT_NOW = '2020-03-13T06:19:00+00:00'
NOT_NOW_DT = datetime.datetime(2020, 3, 13, 6, 19, 00, tzinfo=UTC_TZ)


# We never actually extract compensation 'by id' irl
# for testing purposes we use maas_id though

SELECT_COMPENSATION = """
SELECT
   compensation_id,
   maas_id,
   personal_phone_id,
   created,
   order_id,
   rate,
   max_value,
   min_value,
   compensation_type,
   support_login,
   promocode,
   is_full_refund,
   situation_ids,
   description

FROM grocery_support.compensations
WHERE maas_id = %s
"""

SELECT_COMPENSATION_V2 = """
SELECT
   compensation_id,
   maas_id,
   personal_phone_id,
   created,
   order_id,
   rate,
   max_value,
   min_value,
   is_full_refund,
   compensation_type,
   support_login,
   situation_ids,
   description,
   main_situation_id,
   raw_compensation_info,
   cancel_reason,
   is_promised,
   source,
   error_code,
   main_situation_code
FROM grocery_support.compensations
WHERE maas_id = %s
"""

SELECT_SITUATION = """
SELECT
   situation_id,
   order_id,
   bound_compensation,
   maas_id,
   created,
   products,
   comment,
   source,
   has_photo

FROM grocery_support.situations
WHERE maas_id = %s
"""

SELECT_SITUATION_V2 = """
SELECT
   situation_id,
   order_id,
   bound_compensation,
   maas_id,
   created,
   products_info,
   comment,
   source,
   has_photo,
   situation_code

FROM grocery_support.situations
WHERE maas_id = %s
"""

SELECT_CUSTOMER = """
SELECT
    personal_phone_id,
    comments,
    antifraud_score,
    yandex_uid,
    phone_id,
    eats_user_id
FROM grocery_support.customers
WHERE personal_phone_id = %s
"""

SELECT_ORDER = """
SELECT
    order_id,
    comments
FROM grocery_support.order_info
WHERE order_id = %s
"""

INSERT_COMPENSATION_SQL = """
INSERT INTO grocery_support.compensations (
   compensation_id,
   maas_id,
   personal_phone_id,
   created,
   order_id,
   rate,
   max_value,
   min_value,
   compensation_type,
   support_login,
   promocode,
   is_full_refund,
   situation_ids,
   description
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
     %s,
     %s,
     %s,
     %s,
     %s,
     %s
)
"""

INSERT_COMPENSATION_V2_SQL = """
INSERT INTO grocery_support.compensations (
   compensation_id,
   maas_id,
   personal_phone_id,
   created,
   order_id,
   rate,
   max_value,
   min_value,
   is_full_refund,
   compensation_type,
   support_login,
   situation_ids,
   description,
   main_situation_id,
   raw_compensation_info,
   cancel_reason,
   is_promised,
   source,
   error_code,
   main_situation_code
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
     %s,
     %s,
     %s,
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

INSERT_SITUATION_SQL = """
INSERT INTO grocery_support.situations (
   situation_id,
   order_id,
   bound_compensation,
   maas_id,
   created,
   products,
   comment,
   source,
   has_photo
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

INSERT_SITUATION_V2_SQL = """
INSERT INTO grocery_support.situations (
   situation_id,
   order_id,
   bound_compensation,
   maas_id,
   created,
   products_info,
   comment,
   source,
   has_photo,
   situation_code
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
     %s,
     %s
)
"""

INSERT_CUSTOMER = """
INSERT INTO grocery_support.customers (
    personal_phone_id,
    comments,
    antifraud_score,
    yandex_uid,
    phone_id,
    eats_user_id
    )
VALUES (
    %s, %s, %s, %s, %s, %s
)
"""

INSERT_ORDER = """
INSERT INTO grocery_support.order_info (
    order_id,
    comments
    )
VALUES (
    %s, %s
)
"""


def comments_dict_to_str(some_arr):
    if some_arr is None or some_arr == []:
        return '{}'

    comments_str = ','.join(
        (
            '"(\\"'
            + some['comment']
            + '\\",\\"'
            + some['support_login']
            + '\\",'
            + some['timestamp']
            + ')"'
        )
        for some in some_arr
    )
    return '{' + comments_str + '}'


def product_info_dict_to_str(info):
    if info is None or info == []:
        return '{}'

    return (
        '{"(\\"'
        + info[0]['product_id']
        + '\\",\\"'
        + info[0]['item_price']
        + '\\",\\"'
        + str(info[0]['quantity'])
        + '\\",'
        + info[0]['currency']
        + ')"}'
    )


def product_info_dict_to_pg(info):
    if info is None or info == []:
        return None

    return (
        '{"('
        + info[0]['product_id']
        + ','
        + info[0]['item_price']
        + ','
        + str(info[0]['quantity'])
        + ','
        + info[0]['currency']
        + ')"}'
    )


def str_to_array(some_str):
    if some_str == '{}' or not some_str:
        return []

    some_str = some_str.replace('\\', '')

    current_start = 0
    current_start = some_str.find('(', current_start)
    result = []
    while current_start > 0:
        closing_brace_pos = some_str.find(')', current_start)
        for values_list in csv.reader(
                [some_str[current_start + 1 : closing_brace_pos]],
                skipinitialspace=True,
        ):
            proper_time = datetime.datetime.fromisoformat(
                values_list[2] + ':00',
            ).astimezone(tz=UTC_TZ)
            result.append(
                {
                    'comment': values_list[0],
                    'support_login': values_list[1],
                    'timestamp': proper_time.isoformat(),
                },
            )
        current_start = some_str.find('(', current_start + 1)

    return result


def fix_comments_for_json(comments):
    for comment in comments:
        comment['yandex_login'] = comment['support_login']
        del comment['support_login']


@dataclasses.dataclass
class Compensation:
    def __init__(
            self,
            pgsql,
            maas_id=9,
            compensation_id=str(uuid.uuid4()),
            created=NOW_DT,
            order_id=str(uuid.uuid4()),
            personal_phone_id=str(uuid.uuid4()),
            rate=10,
            max_value=None,
            min_value=None,
            compensation_type='promocode',
            support_login='asdfgh',
            promocode='FREE',
            description=None,
            is_full_refund=False,
            situation_ids=None,
    ):
        self.pg_db = pgsql['grocery_support']
        self.compensation_id = compensation_id
        self.maas_id = maas_id
        self.created = created
        self.order_id = order_id
        self.personal_phone_id = personal_phone_id
        self.rate = rate
        self.max_value = max_value
        self.min_value = min_value
        self.compensation_type = compensation_type
        self.support_login = support_login
        self.promocode = promocode
        self.is_full_refund = is_full_refund
        self.situation_ids = situation_ids
        if self.situation_ids is None:
            self.situation_ids = [str(uuid.uuid4())]
        self.description = description

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_COMPENSATION_SQL,
            [
                self.compensation_id,
                self.maas_id,
                self.personal_phone_id,
                self.created,
                self.order_id,
                self.rate,
                self.max_value,
                self.min_value,
                self.compensation_type,
                self.support_login,
                self.promocode,
                self.is_full_refund,
                self.situation_ids,
                self.description,
            ],
        )

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_COMPENSATION, [self.maas_id])
        result = cursor.fetchone()
        assert result
        (
            compensation_id,
            maas_id,
            personal_phone_id,
            created,
            order_id,
            rate,
            max_value,
            min_value,
            compensation_type,
            support_login,
            promocode,
            is_full_refund,
            situation_ids,
            description,
        ) = result

        self.order_id = order_id
        self.personal_phone_id = personal_phone_id
        self.rate = rate
        self.max_value = max_value
        self.min_value = min_value
        self.compensation_type = compensation_type
        self.support_login = support_login
        self.promocode = promocode
        self.is_full_refund = is_full_refund
        self.compensation_id = str(compensation_id)
        self.maas_id = maas_id
        self.created = created
        self.situation_ids = situation_ids
        self.description = description

    def compare_with_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(SELECT_COMPENSATION, [self.maas_id])
        result = cursor.fetchone()
        assert result
        (
            # uid is generated independently in c++
            _,
            maas_id,
            personal_phone_id,
            # created_at is pain to properly compare
            _,
            order_id,
            rate,
            max_value,
            min_value,
            compensation_type,
            support_login,
            promocode,
            is_full_refund,
            situation_ids,
            description,
        ) = result

        assert len(self.situation_ids) == len(situation_ids)
        assert self.maas_id == maas_id
        assert self.order_id == order_id
        assert self.personal_phone_id == personal_phone_id
        assert self.rate == rate
        assert self.max_value == max_value
        assert self.min_value == min_value
        assert self.compensation_type == compensation_type
        assert self.support_login == support_login
        assert self.promocode == promocode
        assert self.is_full_refund == is_full_refund
        assert self.description == description

    def get_id(self):
        return self.compensation_id

    def get_situations(self):
        return self.situation_ids

    def get_promocode(self):
        return self.promocode

    def response_json(self):
        json_result = {
            'id': self.maas_id,
            'type': self.compensation_type,
            'is_full_refund': self.is_full_refund,
        }
        if self.rate:
            json_result['rate'] = self.rate
        if self.min_value:
            json_result['min_value'] = self.min_value
        if self.max_value:
            json_result['max_value'] = self.max_value

        return json_result


@dataclasses.dataclass
class Situation:
    def __init__(
            self,
            pgsql,
            situation_id=str(uuid.uuid4()),
            maas_id=14,
            created=NOW_DT,
            bound_compensation=None,
            source='ml',
            products=None,
            comment=None,
            has_photo=False,
            order_id='grocery',
    ):
        self.pg_db = pgsql['grocery_support']
        self.situation_id = situation_id
        self.maas_id = maas_id

        self.created = created
        self.bound_compensation = bound_compensation
        self.source = source
        self.products = products
        self.comment = comment
        self.has_photo = has_photo
        self.order_id = order_id

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_SITUATION_SQL,
            [
                self.situation_id,
                self.order_id,
                self.bound_compensation,
                self.maas_id,
                self.created,
                self.products,
                self.comment,
                self.source,
                self.has_photo,
            ],
        )

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_SITUATION, [self.maas_id])
        result = cursor.fetchone()
        assert result
        (
            situation_id,
            order_id,
            bound_compensation,
            maas_id,
            created,
            products,
            comment,
            source,
            has_photo,
        ) = result

        self.bound_compensation = bound_compensation
        self.situation_id = str(situation_id)
        self.products = products
        self.comment = comment
        self.source = source
        self.has_photo = has_photo
        self.maas_id = maas_id
        self.created = created
        self.order_id = order_id

    def compare_with_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(SELECT_SITUATION, [self.maas_id])
        result = cursor.fetchone()
        assert result
        (
            # uid is generated independently in c++
            _,
            order_id,
            # uid is generated independently in c++
            _,
            maas_id,
            # created_at is pain to properly compare
            _,
            products,
            comment,
            source,
            has_photo,
        ) = result

        assert self.maas_id == maas_id
        assert self.products == products
        assert self.comment == comment
        assert self.source == source
        assert self.has_photo == has_photo
        assert self.order_id == order_id

    def get_id(self):
        return self.situation_id

    def get_bound_compensation(self):
        return self.bound_compensation

    def response_json(self):
        json_result = {
            'has_photo': self.has_photo,
            'situation_id': self.maas_id,
            'source': self.source,
        }
        if self.products:
            json_result['goods'] = self.products
        if self.comment:
            json_result['comment'] = self.comment
        return json_result


@dataclasses.dataclass
class Order:
    def __init__(
            self,
            pgsql,
            order_id=str(uuid.uuid4()),
            comments=None,
            status='draft',
    ):
        self.pg_db = pgsql['grocery_support']
        self.order_id = order_id
        self.comments = []
        if comments is not None:
            self.comments = comments
        self.status = status

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_ORDER, [self.order_id])
        result = cursor.fetchone()
        assert result
        (order_id, comments) = result

        assert self.order_id == order_id
        self.comments = str_to_array(comments)

    def compare_with_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_ORDER, [self.order_id])
        result = cursor.fetchone()
        assert result
        (order_id, comments) = result

        assert self.order_id == order_id
        assert self.comments == str_to_array(comments)

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_ORDER, [self.order_id, comments_dict_to_str(self.comments)],
        )

    def json(self):
        json_result = {}
        if self.comments is not None:
            json_result['comments'] = self.comments
            fix_comments_for_json(json_result['comments'])
        return json_result


@dataclasses.dataclass
class Customer:
    def __init__(
            self,
            pgsql,
            personal_phone_id=str(uuid.uuid4()),
            phone_id=str(uuid.uuid4()),
            comments=None,
            antifraud_score='good',
            yandex_uid='super_uid',
            eats_user_id=None,
    ):
        self.pg_db = pgsql['grocery_support']
        self.personal_phone_id = personal_phone_id
        self.antifraud_score = antifraud_score
        self.yandex_uid = yandex_uid
        self.phone_id = phone_id
        self.eats_user_id = eats_user_id
        self.comments = []
        if comments is not None:
            self.comments = comments

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_CUSTOMER, [self.personal_phone_id])
        result = cursor.fetchone()
        assert result
        (
            personal_phone_id,
            comments,
            antifraud_score,
            yandex_uid,
            phone_id,
            eats_user_id,
        ) = result

        assert self.personal_phone_id == personal_phone_id
        self.comments = str_to_array(comments)
        self.antifraud_score = antifraud_score
        self.yandex_uid = yandex_uid
        self.phone_id = phone_id
        self.eats_user_id = eats_user_id

    def compare_with_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_CUSTOMER, [self.personal_phone_id])
        result = cursor.fetchone()
        assert result
        (
            personal_phone_id,
            comments,
            antifraud_score,
            yandex_uid,
            phone_id,
            eats_user_id,
        ) = result

        assert self.personal_phone_id == personal_phone_id
        assert self.antifraud_score == antifraud_score
        assert self.yandex_uid == yandex_uid
        assert self.phone_id == phone_id
        assert self.eats_user_id == eats_user_id
        assert self.comments == str_to_array(comments)

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_CUSTOMER,
            [
                self.personal_phone_id,
                comments_dict_to_str(self.comments),
                self.antifraud_score,
                self.yandex_uid,
                self.phone_id,
                self.eats_user_id,
            ],
        )

    def json(self):
        json_result = {
            'personal_phone_id': self.personal_phone_id,
            'yandex_uid': self.yandex_uid,
            'phone_id': self.phone_id,
            'antifraud_score': self.antifraud_score,
        }

        if self.comments is not None:
            json_result['comments'] = self.comments
            fix_comments_for_json(json_result['comments'])
        if self.eats_user_id is not None:
            json_result['eats_user_id'] = self.eats_user_id

        return json_result


@dataclasses.dataclass
class SituationV2:
    def __init__(
            self,
            pgsql,
            situation_id=str(uuid.uuid4()),
            maas_id=14,
            created=NOW_DT,
            bound_compensation=None,
            source='ml',
            product_infos=None,
            comment=None,
            has_photo=False,
            order_id='grocery',
            situation_code=None,
    ):
        self.pg_db = pgsql['grocery_support']
        self.situation_id = situation_id
        self.maas_id = maas_id

        self.created = created
        self.bound_compensation = bound_compensation
        self.source = source
        self.product_infos = product_infos
        self.comment = comment
        self.has_photo = has_photo
        self.order_id = order_id
        self.situation_code = situation_code

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_SITUATION_V2_SQL,
            [
                self.situation_id,
                self.order_id,
                self.bound_compensation,
                self.maas_id,
                self.created,
                product_info_dict_to_str(self.product_infos),
                self.comment,
                self.source,
                self.has_photo,
                self.situation_code,
            ],
        )

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_SITUATION_V2, [self.maas_id])
        result = cursor.fetchone()
        assert result
        (
            situation_id,
            order_id,
            bound_compensation,
            maas_id,
            created,
            product_infos,
            comment,
            source,
            has_photo,
            situation_code,
        ) = result

        self.bound_compensation = bound_compensation
        self.situation_id = str(situation_id)
        self.product_infos = product_infos
        self.comment = comment
        self.source = source
        self.has_photo = has_photo
        self.maas_id = maas_id
        self.created = created
        self.order_id = order_id
        self.situation_code = situation_code

    def compare_with_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(SELECT_SITUATION_V2, [self.maas_id])
        result = cursor.fetchone()
        assert result
        (
            # uid is generated independently in c++
            _,
            order_id,
            # uid is generated independently in c++
            _,
            maas_id,
            # created_at is pain to properly compare
            _,
            product_infos,
            comment,
            source,
            has_photo,
            situation_code,
        ) = result

        assert self.maas_id == maas_id
        assert product_info_dict_to_pg(self.product_infos) == product_infos
        assert self.comment == comment
        assert self.source == source
        assert self.has_photo == has_photo
        assert self.order_id == order_id
        assert self.situation_code == situation_code

    def get_id(self):
        return self.situation_id

    def get_bound_compensation(self):
        return self.bound_compensation


@dataclasses.dataclass
class CompensationV2:
    def __init__(
            self,
            pgsql,
            maas_id=9,
            compensation_id=str(uuid.uuid4()),
            created=NOW_DT,
            order_id=str(uuid.uuid4()),
            personal_phone_id=str(uuid.uuid4()),
            rate=10,
            max_value=None,
            min_value=None,
            is_full_refund=False,
            compensation_type='promocode',
            support_login='test_login',
            description=None,
            situation_ids=None,
            main_situation_id=None,
            raw_compensation_info=None,
            cancel_reason=None,
            is_promised=False,
            source=None,
            error_code=None,
            main_situation_code=None,
    ):
        self.pg_db = pgsql['grocery_support']
        self.compensation_id = compensation_id
        self.maas_id = maas_id
        self.created = created
        self.order_id = order_id
        self.personal_phone_id = personal_phone_id
        self.rate = rate
        self.max_value = max_value
        self.min_value = min_value
        self.is_full_refund = is_full_refund
        self.compensation_type = compensation_type
        self.support_login = support_login
        self.situation_ids = situation_ids
        if self.situation_ids is None:
            self.situation_ids = [str(uuid.uuid4())]
        self.description = description
        self.main_situation_id = main_situation_id
        self.raw_compensation_info = raw_compensation_info
        self.cancel_reason = cancel_reason
        self.is_promised = is_promised
        self.source = source
        self.error_code = error_code
        self.main_situation_code = main_situation_code

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_COMPENSATION_V2_SQL,
            [
                self.compensation_id,
                self.maas_id,
                self.personal_phone_id,
                self.created,
                self.order_id,
                self.rate,
                self.max_value,
                self.min_value,
                self.is_full_refund,
                self.compensation_type,
                self.support_login,
                self.situation_ids,
                self.description,
                self.main_situation_id,
                self.raw_compensation_info,
                self.cancel_reason,
                self.is_promised,
                self.source,
                self.error_code,
                self.main_situation_code,
            ],
        )

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_COMPENSATION_V2, [self.maas_id])
        result = cursor.fetchone()
        assert result
        (
            compensation_id,
            maas_id,
            personal_phone_id,
            created,
            order_id,
            rate,
            max_value,
            min_value,
            is_full_refund,
            compensation_type,
            support_login,
            situation_ids,
            description,
            main_situation_id,
            raw_compensation_info,
            cancel_reason,
            is_promised,
            source,
            error_code,
            main_situation_code,
        ) = result

        self.order_id = order_id
        self.personal_phone_id = personal_phone_id
        self.rate = rate
        self.max_value = max_value
        self.min_value = min_value
        self.is_full_refund = is_full_refund
        self.compensation_type = compensation_type
        self.support_login = support_login
        self.compensation_id = str(compensation_id)
        self.maas_id = maas_id
        self.created = created
        self.situation_ids = situation_ids
        self.description = description
        self.main_situation_id = main_situation_id
        self.raw_compensation_info = json.dumps(raw_compensation_info)
        self.cancel_reason = cancel_reason
        self.is_promised = is_promised
        self.source = source
        self.error_code = error_code
        self.main_situation_code = main_situation_code

    def compare_with_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(SELECT_COMPENSATION_V2, [self.maas_id])
        result = cursor.fetchone()
        assert result
        (
            # uid is generated independently in c++
            _,
            maas_id,
            personal_phone_id,
            # created_at is pain to properly compare
            _,
            order_id,
            rate,
            max_value,
            min_value,
            is_full_refund,
            compensation_type,
            support_login,
            situation_ids,
            description,
            main_situation_id,
            raw_compensation_info,
            cancel_reason,
            is_promised,
            source,
            error_code,
            main_situation_code,
        ) = result

        assert len(self.situation_ids) == len(situation_ids)
        assert self.maas_id == maas_id
        assert self.order_id == order_id
        assert self.personal_phone_id == personal_phone_id
        assert self.rate == rate
        assert self.max_value == max_value
        assert self.min_value == min_value
        assert self.is_full_refund == is_full_refund
        assert self.compensation_type == compensation_type
        assert self.support_login == support_login
        assert self.description == description
        assert str(self.main_situation_id) == str(main_situation_id)
        assert json.loads(self.raw_compensation_info) == raw_compensation_info
        assert self.cancel_reason == cancel_reason
        assert self.is_promised == is_promised
        assert self.source == source
        assert self.error_code == error_code
        assert self.main_situation_code == main_situation_code

    def get_id(self):
        return self.compensation_id

    def get_situations(self):
        return self.situation_ids
