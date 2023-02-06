import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.internal import card_operations

from cardstorage_mock import mock_cardstorage


@pytest.mark.parametrize('card_id,found', [
    ('card-x5619', True),
    ('card-x5691', False)
])
@pytest.inline_callbacks
def test_get_cards(patch, card_id, found):
    @patch('taxi.external.cardstorage.get_payment_methods')
    @async.inline_callbacks
    def cardstorage_get_cards(request, log_extra=None):
        yield
        assert not hasattr(request, 'service_type')
        assert request.yandex_uid == '123'
        async.return_value([{
            'currency': 'RUB',
            'card_id': 'card-x5619',
            'billing_card_id': 'x5619',
            'from_db': False,
            'number': '411111****1111',
            'system': 'VISA',
            'valid': True,
            'expiration_month': 11,
            'expiration_year': 2022,
            'owner': '123',
            'persistent_id': 'card1234',
            'service_labels': ['taxi:persistent_id:card1234'],
            'possible_moneyless': False,
            'region_id': '225',
            'regions_checked': ['225'],
        }])

    if not found:
        with pytest.raises(card_operations.InvalidCardError):
            yield card_operations.get_card(
                card_id, '123', log_extra=None
            )
    else:
        card = yield card_operations.get_card(
            card_id, '123', log_extra=None
        )
        assert card.owner == '123'
        assert card.card_id == card_id
        assert card.system == 'VISA'
        assert card.number == '411111****1111'
        assert card.billing_card_id == 'x5619'
        assert card.currency == 'RUB'
        assert card.name == ''
        assert card.blocking_reason == ''
        assert card.valid is True
        assert card.regions_checked == [225]
        assert card.possible_moneyless is False
        assert card._updated_from_db is False
        assert card.service_labels == {'taxi:persistent_id:card1234'}
        assert card.persistent_id == 'card1234'


@pytest.mark.parametrize('provided_service, expected_service', [
    ('card', 'card'),
    ('uber', 'uber'),
    ('uber_roaming', 'uber_roaming')
])
@pytest.inline_callbacks
def test_check_card(patch, provided_service, expected_service):
    UID = 'uid1'
    USER_IP = '1.1.1.1'
    CARD_ID = '96061800'
    CARD_PAYMENT_ID = 'card-96061800'
    CARD_SYSTEM = 'Visa'
    CARD_NUMBER = '555555****4444'
    LOG_EXTRA = {'link': '123'}

    @patch('taxi.external.billing.check_card')
    @async.inline_callbacks
    def check_card(yandex_uid, billing_card_id, user_ip=None, region_id=None,
                   currency=None, timeout=None, service=None, uber_uid=None,
                   log_extra=None):
        yield
        async.return_value(True)

    card = card_operations.create_card_object(
        UID, CARD_ID, CARD_SYSTEM, CARD_NUMBER, CARD_PAYMENT_ID,
        settings.DEFAULT_CURRENCY
    )
    valid = yield card.check(log_extra=LOG_EXTRA)
    assert valid
    valid = yield card.check(user_ip=USER_IP, region_id=225, currency='RUB',
                             service=provided_service, log_extra=LOG_EXTRA)
    assert valid

    assert check_card.calls == [
        {
            'args': (UID, CARD_PAYMENT_ID),
            'kwargs': {
                'user_ip': None,
                'region_id': None,
                'currency': None,
                'timeout': settings.BILLING_CHECK_CARD_TIMEOUT,
                'service': None,
                'uber_uid': None,
                'log_extra': LOG_EXTRA,
            }
        },
        {
            'args': (UID, CARD_PAYMENT_ID),
            'kwargs': {
                'user_ip': USER_IP,
                'region_id': 225,
                'currency': 'RUB',
                'timeout': settings.BILLING_CHECK_CARD_TIMEOUT,
                'service': expected_service,
                'uber_uid': None,
                'log_extra': LOG_EXTRA,
            }
        },
    ]


@pytest.inline_callbacks
def test_get_card_from_db(patch):
    mock_cardstorage(patch)
    card = yield card_operations.get_card_from_db('yandex_uid', 'card-1234')
    assert card.card_id == 'card-1234'
    assert card.billing_card_id == '1234'
    assert card.owner == 'yandex_uid'
    assert not card.unbound


@pytest.inline_callbacks
def test_get_card_from_db_notfound(patch):
    mock_cardstorage(patch)
    with pytest.raises(card_operations.CardNotFoundError):
        yield card_operations.get_card_from_db('yandex_uid', 'does not exist')


@pytest.inline_callbacks
def test_get_card_from_db_unbound(patch):
    mock_cardstorage(patch)
    card = yield card_operations.get_card_from_db(
        'yandex_uid', 'card-unbound',
    )
    assert card.unbound


@pytest.mark.filldb(cards='regions_checked')
@pytest.inline_callbacks
def test_card_regions_checked(patch):
    mock_cardstorage(patch)

    card = yield card_operations.get_card_from_db('yandex_uid', 'card-1234')
    assert card.was_region_checked(225)
    assert not card.was_region_checked(333)

    yield card.mark_as_checked(333)

    card = yield card_operations.get_card_from_db('yandex_uid', 'card-1234')
    assert card.was_region_checked(225)
    assert card.was_region_checked(333)

    yield card.mark_as_checked(225, False)
    card = yield card_operations.get_card_from_db('yandex_uid', 'card-1234')
    assert not card.was_region_checked(225)
    assert card.was_region_checked(333)


@pytest.inline_callbacks
def is_busy(card):
    updated = yield card_operations.get_card_from_db(
        card.owner, card.card_id)
    async.return_value(bool(updated.busy_with))


@pytest.inline_callbacks
def test_mark_as_busy(patch):
    mock_cardstorage(patch)

    UID = 'uid1'
    CARD_BILLING_ID = '96061800'
    CARD_PAYMENT_ID = 'card-96061800'
    CARD_SYSTEM = 'Visa'
    CARD_NUMBER = '555555****4444'
    ORDER_1 = 'first_order'
    ORDER_2 = 'second_order'

    card = card_operations.create_card_object(
        UID, CARD_PAYMENT_ID, CARD_SYSTEM, CARD_NUMBER, CARD_BILLING_ID,
        settings.DEFAULT_CURRENCY,
        service_labels=['taxi:persistent_id:123456'],
        persistent_id='123456'
    )

    yield card.mark_as_busy(ORDER_1)
    assert (yield is_busy(card))

    yield card.mark_as_busy(ORDER_1)  # to check repeat operation
    yield card.mark_as_busy(ORDER_2)

    assert (yield is_busy(card))


@pytest.inline_callbacks
def test_unmark_as_busy(patch):
    ORDER_1 = 'order1'
    ORDER_2 = 'order2'

    mock_cardstorage(patch)

    card = yield card_operations.get_card_from_db('yandex_uid', 'card-1234')

    yield card.unmark_as_busy(ORDER_1)
    assert (yield is_busy(card))
    yield card.unmark_as_busy(ORDER_2)
    assert not (yield is_busy(card))


@pytest.mark.parametrize('card1,card2,uid,expected', [
    ('card-x1234', 'card-x1234567890', 'uid1', True),
    ('card-x1234', 'card-x1234', 'uid1', True),
    ('card-x1234567890', 'card-x1234567890', 'uid1', True),
    ('card-x1234567890', 'card-x1234', 'uid1', True),
    ('card-x1234', 'card-x1234567890', 'uid2', False),
    ('card-x1234567890', 'card-x1234', 'uid2', False),
    ('card-x5678', 'card-x5678', 'uid2', True),
    ('card-x5678', 'card-x-junk', 'uid3', False),
    ('card-x5678', 'card-x0987', 'uid3', False),
    ('card-x5678', 'card-x1234567890', 'uid3', False),
    ('card-x0987', 'card-x1234567890', 'uid2', False),
    ('card-x0987', 'card-x1234567890', 'uid3', True),
    ('card-x0987', 'card-x5678', 'uid3', False),
    ('card-x0987', '', 'uid3', False),
    ('card-x0987', None, 'uid3', False),
])
@pytest.inline_callbacks
def test_is_same_card(patch, card1, card2, uid, expected):
    mock_cardstorage(patch)
    assert expected == (yield card_operations.is_same_card(card1, card2, uid))
