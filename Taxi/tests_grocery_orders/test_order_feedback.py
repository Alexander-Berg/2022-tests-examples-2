import uuid

import pytest

from . import configs
from . import consts
from . import headers
from . import models


CREATE_TICKETS_EVALUATION_THRESHOLD = 3
DEFAULT_EVALUATION = 1

HANDLERS = ['/lavka/v1/orders/v1/feedback', '/lavka/v1/orders/v2/feedback']

COMMENT_ID_KEYS = {
    'comment_id_1': 'comment_key_1',
    'comment_id_2': 'comment_key_2',
}

COMMENT_TRANSLATIONS = {
    'comment_key_1': {'ru': 'Ключ номер 1'},
    'comment_key_2': {'ru': 'Ключ номер 2'},
}

MACRO_ID = 63354

USER_INFO = {
    'order_id': 'some_order_id',
    'yandex_uid': headers.YANDEX_UID,
    'taxi_user_id': headers.USER_ID,
    'eats_user_id': headers.EATS_USER_ID,
    'personal_phone_id': headers.PERSONAL_PHONE_ID,
    'app_info': headers.APP_INFO,
    'locale': 'ru',
    'country_iso3': 'RUS',
    'region_id': 7,
}


def _get_comment_translation(comment_id, locale='ru'):
    return COMMENT_TRANSLATIONS[COMMENT_ID_KEYS[comment_id]][locale]


GROCERY_FEEDBACK_PREDEFINED_COMMENTS = pytest.mark.experiments3(
    name='grocery_feedback_predefined_comments',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'options': [
                    {
                        'evaluation': 1,
                        'title': '1 Star',
                        'predefined_comments': [
                            {
                                'comment_id': 'comment_id_1',
                                'eats_id': 1,
                                'tanker_key': COMMENT_ID_KEYS['comment_id_1'],
                            },
                        ],
                    },
                    {
                        'evaluation': 2,
                        'title': '2 Stars',
                        'predefined_comments': [
                            {
                                'comment_id': 'comment_id_2',
                                'eats_id': 1,
                                'tanker_key': COMMENT_ID_KEYS['comment_id_2'],
                            },
                        ],
                    },
                ],
            },
        },
    ],
    is_config=True,
)


def _get_init_chat_matched(evaluation, feedback_options, comment):
    evaluation_matched = evaluation in [4, 5]
    feedback_options_matched = False
    if feedback_options is not None:
        feedback_options_matched = 'Качество продуктов' in feedback_options
    no_comment = comment is None or comment == ''

    return evaluation_matched and feedback_options_matched and no_comment


def _get_order_feedback(pgsql, order_id):
    cursor = pgsql['grocery_orders'].cursor()

    cursor.execute(
        'SELECT feedback_options, comment '
        f'FROM orders.feedback where order_id = \'{order_id}\'',
    )

    return cursor.fetchone()


@pytest.mark.parametrize('evaluation', [1, 2, 3, 4, 5])
@pytest.mark.parametrize(
    'feedback_options',
    [None, ['Долгая Доставка', 'Невежливый Курьер', 'Качество продуктов'], []],
)
@pytest.mark.parametrize('comment', [None, '', 'Растаяла мороженка'])
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        tracker,
        grocery_depots,
        experiments3,
        processing,
        evaluation,
        feedback_options,
        comment,
):
    configs.set_feedback_processing_rules(
        experiments3=experiments3,
        evaluation_threshold=CREATE_TICKETS_EVALUATION_THRESHOLD,
        creating_tickets_enabled=True,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_tags=consts.TICKET_TAGS,
        create_chatterbox_ticket=True,
        macro_id=MACRO_ID,
    )

    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status='closed',
    )

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        country_iso3=USER_INFO['country_iso3'],
        region_id=USER_INFO['region_id'],
    )

    if evaluation <= CREATE_TICKETS_EVALUATION_THRESHOLD:
        tracker.set_request_data(
            order_id=order.order_id,
            queue=consts.TICKET_QUEUE,
            summary='Обратная связь по заказу',
            tags=consts.TICKET_TAGS,
            create_chatterbox_ticket=True,
        )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/feedback',
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'refused_feedback': False,
            'feedback': {
                'evaluation': evaluation,
                'feedback_options': feedback_options,
                'comment': comment,
            },
        },
    )

    assert response.status_code == 200

    order.update()

    assert order.feedback_status == 'submitted'
    assert order.evaluation == evaluation

    if (
            feedback_options is None or feedback_options == []
    ) and comment is None:
        assert not _get_order_feedback(pgsql, order.order_id)
    else:
        feedback = _get_order_feedback(pgsql, order.order_id)
        assert feedback[0] == feedback_options
        assert feedback[1] == comment

    no_comment = comment is None or comment == ''
    no_options = feedback_options is None or feedback_options == []
    init_chat_matched = _get_init_chat_matched(
        evaluation, feedback_options, comment,
    )
    if (
            evaluation > CREATE_TICKETS_EVALUATION_THRESHOLD
            and no_options
            and no_comment
    ) or init_chat_matched:
        assert tracker.times_called() == 0
    else:
        assert tracker.times_called() == 1

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    if init_chat_matched:
        assert len(events) == 1
        payload = events[0].payload
        code = 'feedback'
        assert payload['order_id'] == order.order_id
        assert payload['reason'] == 'create_support_chat'
        assert payload['macro_id'] == MACRO_ID
        assert payload['code'] == code
        assert (
            events[0].idempotency_token
            == 'create-support-chat-{}{}'.format(order.order_id, code)
        )
    else:
        assert not events


@pytest.mark.translations(grocery_orders=COMMENT_TRANSLATIONS)
@GROCERY_FEEDBACK_PREDEFINED_COMMENTS
@pytest.mark.parametrize('evaluation', [1, 2, 3, 4, 5])
@pytest.mark.parametrize(
    'predefined_comments',
    [
        None,
        [{'comment_id': 'comment_id_1'}, {'comment_id': 'comment_id_2'}],
        [],
    ],
)
@pytest.mark.parametrize('comment', [None, 'Растаяла мороженка'])
async def test_basic_v2(
        taxi_grocery_orders, pgsql, evaluation, predefined_comments, comment,
):
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status='closed',
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/feedback',
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'refused_feedback': False,
            'feedback': {
                'evaluation': evaluation,
                'predefined_comments': predefined_comments,
                'comment': comment,
            },
        },
    )

    assert response.status_code == 200

    order.update()

    assert order.feedback_status == 'submitted'
    assert order.evaluation == evaluation

    if (
            predefined_comments is None or predefined_comments == []
    ) and comment is None:
        assert not _get_order_feedback(pgsql, order.order_id)
    else:
        feedback = _get_order_feedback(pgsql, order.order_id)

        expected_comments = None
        if predefined_comments is not None:
            expected_comments = [
                _get_comment_translation(comment['comment_id'])
                for comment in predefined_comments
            ]

        assert feedback[0] == expected_comments
        assert feedback[1] == comment


@pytest.mark.parametrize('evaluation', [1, 3, 4, 5])
@pytest.mark.parametrize('creating_tickets_enabled', [True, False])
@pytest.mark.parametrize('create_chatterbox_ticket', [True, False])
async def test_ticket_creation_flow(
        taxi_grocery_orders,
        pgsql,
        tracker,
        grocery_depots,
        experiments3,
        evaluation,
        creating_tickets_enabled,
        create_chatterbox_ticket,
):
    configs.set_feedback_processing_rules(
        experiments3=experiments3,
        evaluation_threshold=CREATE_TICKETS_EVALUATION_THRESHOLD,
        creating_tickets_enabled=creating_tickets_enabled,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_tags=consts.TICKET_TAGS,
        create_chatterbox_ticket=create_chatterbox_ticket,
    )

    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status='closed',
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    if creating_tickets_enabled:
        tracker.set_request_data(
            order_id=order.order_id,
            queue=consts.TICKET_QUEUE,
            summary='Обратная связь по заказу',
            tags=consts.TICKET_TAGS,
            create_chatterbox_ticket=create_chatterbox_ticket,
        )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/feedback',
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'refused_feedback': False,
            'feedback': {
                'evaluation': evaluation,
                'feedback_options': ['Долгая Доставка', 'Невежливый Курьер'],
                'comment': 'Растаяла мороженка',
            },
        },
    )

    assert response.status_code == 200

    order.update()

    assert order.feedback_status == 'submitted'
    assert order.evaluation == evaluation

    assert tracker.times_called() == (1 if creating_tickets_enabled else 0)


async def test_ticket_creation_fallback_locale(
        taxi_grocery_orders, pgsql, tracker, experiments3, grocery_depots,
):
    configs.set_feedback_processing_rules(
        experiments3=experiments3,
        evaluation_threshold=CREATE_TICKETS_EVALUATION_THRESHOLD,
        creating_tickets_enabled=True,
        ticket_queue=consts.TICKET_QUEUE,
        ticket_tags=consts.TICKET_TAGS,
        create_chatterbox_ticket=True,
    )

    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status='closed',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    tracker.set_request_data(
        order_id=order.order_id,
        queue=consts.TICKET_QUEUE,
        summary='Обратная связь по заказу',
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/feedback',
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'refused_feedback': False,
            'feedback': {'evaluation': DEFAULT_EVALUATION},
        },
    )

    assert response.status_code == 200

    order.update()

    assert order.feedback_status == 'submitted'
    assert order.evaluation == DEFAULT_EVALUATION

    assert tracker.times_called() == 1


@pytest.mark.parametrize('handler', HANDLERS)
@pytest.mark.parametrize('evaluation', [1, None])
@pytest.mark.parametrize('feedback_options', [None, ['Долгая доставка']])
@pytest.mark.parametrize('comment', [None, 'Растаяла мороженка'])
async def test_refused(
        taxi_grocery_orders,
        pgsql,
        tracker,
        handler,
        evaluation,
        feedback_options,
        comment,
):
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status='closed',
    )

    feedback_passed = (
        evaluation is not None
        or feedback_options is not None
        or comment is not None
    )

    response = await taxi_grocery_orders.post(
        handler,
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'refused_feedback': True,
            'feedback': (
                {
                    'evaluation': evaluation,
                    'feedback_options': feedback_options,
                    'predefined_comments': (
                        [{'comment_id': option} for option in feedback_options]
                        if feedback_options is not None
                        else None
                    ),
                    'comment': comment,
                }
                if feedback_passed
                else None
            ),
        },
    )

    order.update()
    if feedback_passed:
        assert response.status_code == 400
        assert order.feedback_status is None
    else:
        assert response.status_code == 200
        assert order.feedback_status == 'refused'

    assert order.evaluation is None
    assert not _get_order_feedback(pgsql, order.order_id)

    assert tracker.times_called() == 0


@pytest.mark.parametrize('handler', HANDLERS)
async def test_order_not_present(taxi_grocery_orders, pgsql, handler):
    non_existing_order_id = str(uuid.uuid4())

    response = await taxi_grocery_orders.post(
        handler,
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': non_existing_order_id,
            'refused_feedback': False,
            'feedback': {
                'evaluation': 1,
                'feedback_options': ['hello'],
                'comment': 'there',
            },
        },
    )

    assert response.status_code == 404
    assert not _get_order_feedback(pgsql, non_existing_order_id)


@pytest.mark.parametrize('handler', HANDLERS)
@pytest.mark.parametrize('evaluation', [0, 6, -1])
async def test_invalid_evaluation(
        taxi_grocery_orders, pgsql, evaluation, handler,
):
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status='closed',
    )

    response = await taxi_grocery_orders.post(
        handler,
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'refused_feedback': False,
            'feedback': {'evaluation': evaluation},
        },
    )

    assert response.status_code == 400

    order.update()

    assert order.feedback_status is None
    assert order.evaluation is None
    assert not _get_order_feedback(pgsql, order.order_id)


@pytest.mark.parametrize('handler', HANDLERS)
@pytest.mark.parametrize(
    'order_status',
    [
        'draft',
        'checked_out',
        'reserving',
        'reserved',
        'assembling',
        'assembled',
        'delivering',
        'canceled',
        'pending_cancel',
    ],
)
async def test_order_not_closed(
        taxi_grocery_orders, pgsql, order_status, handler,
):
    order = models.Order(
        pgsql=pgsql,
        state=models.OrderState(close_money_status='success'),
        status=order_status,
    )

    response = await taxi_grocery_orders.post(
        handler,
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'refused_feedback': False,
            'feedback': {
                'evaluation': 1,
                'feedback_options': ['hello'],
                'comment': 'there',
            },
        },
    )

    assert response.status_code == 400
    assert not _get_order_feedback(pgsql, order.order_id)
