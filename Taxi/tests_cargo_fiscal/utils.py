TOPIC_ID = 'topic_id'
INTERNAL_TOPIC_ID = 3
UNREADY_TOPIC_ID = 'unready_topic_id'
INTERNAL_UNREADY_TOPIC_ID = 4
TRANSACTION_ID = 'transaction_id'
URL = 'url'


def _get_create_record_request(topic_id, transaction_id, url):
    return f"""
        INSERT INTO
            cargo_fiscal.transaction
                (topic_id, transaction_id, url, context)
        VALUES ({topic_id}, \'{transaction_id}\', \'{url}\',
        '{{"is_refund": false, "payment_method": "card",
        "transaction_id": "{transaction_id}"}}')
        ON CONFLICT (topic_id, transaction_id) DO UPDATE
            SET
                topic_id = excluded.topic_id,
                transaction_id = excluded.transaction_id,
                url = \'{url}\',
                context = '{{"is_refund": false,
                "payment_method": "card",
                "transaction_id": "{transaction_id}"}}'
            WHERE transaction.topic_id = {topic_id} and
            transaction.transaction_id = \'{transaction_id}\';"""


def create_record(pgsql):
    cursor = pgsql['cargo_fiscal'].conn.cursor()

    cursor.execute(
        f"""INSERT INTO cargo_fiscal.topic (id, consumer, domain, topic_id, context)
    VALUES ({INTERNAL_TOPIC_ID}, 'delivery', 'orders',
    '{TOPIC_ID}', '{{"title": "Услуги курьерской доставки",
    "country": "RUS", "provider_inn": "381805387129",
    "service_rendered_at": "2022-03-03T14:25:49.233+00:00"}}')""",
    )

    cursor.execute(
        _get_create_record_request(INTERNAL_TOPIC_ID, TRANSACTION_ID, URL),
    )

    cursor.close()


def _get_create_unredy_record_request(topic_id, transaction_id):
    return f"""
        INSERT INTO
            cargo_fiscal.transaction
                (topic_id, transaction_id, context)
        VALUES ({topic_id}, \'{transaction_id}\',
        '{{"is_refund": false, "payment_method": "card",
        "transaction_id": "{transaction_id}"}}');"""


def create_unready_record(pgsql):
    cursor = pgsql['cargo_fiscal'].conn.cursor()

    cursor.execute(
        f"""INSERT INTO cargo_fiscal.topic (id, consumer, domain, topic_id, context)
    VALUES ({INTERNAL_UNREADY_TOPIC_ID}, 'delivery', 'orders',
    '{UNREADY_TOPIC_ID}', '{{"title": "Услуги курьерской доставки",
    "country": "RUS", "provider_inn": "381805387129",
    "service_rendered_at": "2022-03-03T14:25:49.233+00:00"}}')""",
    )

    cursor.execute(
        _get_create_unredy_record_request(
            INTERNAL_UNREADY_TOPIC_ID, TRANSACTION_ID,
        ),
    )

    cursor.close()
