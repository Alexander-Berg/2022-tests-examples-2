from unittest import TestCase
from support_etl.layer.yt.ods.support_moderation.common.impl import macro_lang_from_tags, actions_macro


class TestSupportModerationImpl(TestCase):
    def test_macro_lang_from_tags(self):
        self.assertEqual(
            macro_lang_from_tags(['lang_ru', 'whiteplates_switch_to_cash', 'promo_given']),
            'ru'
        )
        self.assertEqual(
            macro_lang_from_tags(['rd_feedback_driver_or_vehicle', 'язык_армянский', 'клиент_оплата']),
            'hy'
        )
        self.assertEqual(
            macro_lang_from_tags([
                "закрыто_на_модерации",
                "users_другое",
                "как_это_работает",
                "access_free",
                "intl",
                "rd_payment_type_card_add"
            ]),
            None
        )

    def test_actions_macro(self):

        self.assertEqual(
            actions_macro('''Bonjour! \nMerci pour votre retour. Veuillez accepter nos excuses et ce code 
promotionnel {{promo:1/2/3/4/5}}, d'un montant de {{nominal}} {{currency}} Vous devez le rentrer 
dans la section \" Code promotionnel \" du menu de l'application avant de passer un commande.'''),
            {'refund': False, 'promocode': True}
        )
        self.assertEqual(
            actions_macro('''. משום שהוא לא עשה זאת, נמשיך לעקוב אחר שאר המשובים על עבודתו. 
החיוב עבור ההזמנה הזו בוטל. {{refund_hide:0:PAID_CANCEL_DRIVE}}'''),
            {'refund': True, 'promocode': False}
        )
        self.assertEqual(
            actions_macro('''Мне жаль, что водитель перепутал пассажиров и не выполнил заказ. 
Списание уже отменено. {{refund_hide:0:OTHER_USER}}
Мы очень признательны, что вы делаете наш сервис лучше, поэтому хотим подарить 
вам промокод {{promo}} на {{nominal}} {{currency}} на следующую поездку. '''),
            {'refund': True, 'promocode': True}
        )
        self.assertEqual(
            actions_macro('''Проверили ваш заказ — деньги действительно были зарезервированы на карте. 
Передали информацию коллегам, будем разбираться. Операция отменена, скоро деньги вернутся на счёт. 
Простите за неудобства, пожалуйста.'''),
            {'refund': False, 'promocode': False}
        )
