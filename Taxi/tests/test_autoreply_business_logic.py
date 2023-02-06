# coding: utf-8

from taxi_pyml.autoreply import probs_postprocessor

# Classes for promocodes.
BL_CLASSES = {
    'cancel_classes': {'cancel_cash': '49066', 'cancel_card': '49069'},
    'surge_promo': {'surge_all': '21901'},
    'details': {'all_details': '5679'},
    'check_info': {'check_cash': '17852', 'check_card': '6075'},
    'paid_cancel': {
        'cancel_client_card': '49340',
        'order_accidently_card': '49494',
    },
    'end_instead_cancel': {
        'end_cash': '18436',
        'end_card': '18396',
        'end_cash_without_charge': '20084',
    },
    'double_pay': {
        'pay_card_without_charge': '5811',
        'pay_card_debt': '16942',
    },
}
# Name of cash type payment
TYPE_PAID_CASH = 'способ_оплаты_нал'
# Name of card type payment
TYPE_PAID_CARD = 'способ_оплаты_карта'
# Class and reason name, if foc ticket need details but we want ab experiment.
CLASS_REASON_FOC_AB = 'bl_foc_ab'
# Class and reason name, if cancel macro does not correspond to business logic
CLASS_REASON_BL_CANCEL_CLASS = 'bl_cancel_class'


class TestReasonPostprocessor:
    def test_check_info_card2cash(self):
        assert (
            probs_postprocessor.check_check_info(
                {'payment_type': TYPE_PAID_CASH},
                BL_CLASSES['check_info']['check_card'],
            )
            == BL_CLASSES['check_info']['check_cash']
        )

    def test_paid_cancel_dont_get(self):
        assert (
            probs_postprocessor.check_business_logic_cancel_paid(
                {'payment_type': TYPE_PAID_CARD, 'paid_cancel_tag': False},
                BL_CLASSES['cancel_classes']['cancel_cash'],
                {'wide_cancel': True},
            )
            == CLASS_REASON_BL_CANCEL_CLASS
        )

    def test_paid_cancel_card2cash(self):
        assert (
            probs_postprocessor.check_business_logic_cancel_paid(
                {
                    'payment_type': TYPE_PAID_CASH,
                    'paid_cancel_tag': False,
                    'cancel_time': 120.0,
                },
                BL_CLASSES['cancel_classes']['cancel_card'],
                {'wide_cancel': True},
            )
            == BL_CLASSES['cancel_classes']['cancel_cash']
        )

    def test_foc(self):
        assert (
            probs_postprocessor.check_foc(
                {'request_id': TYPE_PAID_CARD},
                BL_CLASSES['details']['all_details'],
            )
            == CLASS_REASON_FOC_AB
        )
