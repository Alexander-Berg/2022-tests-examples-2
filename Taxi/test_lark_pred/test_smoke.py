# flake8: noqa
# pylint: disable=too-many-lines
import pypred

import pytest

from supportai_lib import predicate


@pytest.mark.parametrize(
    'predicate_rule', ['undefined is undefined', 'some is undefined'],
)
async def test_smoke(predicate_rule):
    pypred_predicate = pypred.Predicate(predicate_rule)
    lark_predicate = predicate.Predicate(predicate_rule)

    pypred_result = pypred_predicate.evaluate({})
    lark_result = lark_predicate.evaluate({})

    assert pypred_result == lark_result


@pytest.mark.parametrize(
    'predicate_rule',
    [
        """
        activity_decrease > 0
        and number_of_reopens = 0
        and (manualactivitylast24hours is false or manualactivitylast24hours is undefined )
        and not antifraud_rules contains 'chatterbox_message_fraud'
        and driver_activity_return_count < 2
        and return_activity is not true
        and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        and number_of_characters < 850
        and not line = 'taxi_logistic_ml'
        and (comment_lowercased contains  'нецензур' or
        comment_lowercased contains  ' орет' or
        comment_lowercased contains  ' орёт' or
        comment_lowercased contains  ' хам' or
        comment_lowercased contains  'поругал' or
        comment_lowercased contains  'матом' or
        comment_lowercased contains  'кричат' or
        comment_lowercased contains  'груб' or
        comment_lowercased contains  'конфликт' or
        comment_lowercased contains  'спор' or
        comment_lowercased contains  'нагл' or
        comment_lowercased contains  'истери' or
        comment_lowercased contains  'качать права' or
        comment_lowercased contains  'неадекват' or
        comment_lowercased contains  'скандал' or
        comment_lowercased contains  'оскорб' or
        comment_lowercased contains  'оскарб' or
        comment_lowercased contains  'ругается' or
        comment_lowercased contains  'ругаться' or
        comment_lowercased contains  ' агрес') and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        number_of_reopens > 0
        and success_order_flg is true
        and final_ride_duration < 120
        and tariff != 'walking_courier'
        and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        and number_of_characters < 850
        and not all_tags contains 'макрос_мл_макрос_субсидия_2мин'
        and not all_tags contains 'макрос_мл_макрос_субсидия_меньше_двух_мин_реопен'
        and not line = 'taxi_logistic_ml' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        number_of_reopens > 0
        and success_order_flg is true
        and final_ride_duration < 120
        and tariff != 'walking_courier'
        and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        and number_of_characters < 850
        and not all_tags contains 'макрос_мл_макрос_субсидия_меньше_двух_мин_второй_вар_реопен'
        and not line = 'taxi_logistic_ml' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        activity_decrease > 0 and number_of_reopens = 0 and driver_activity_return_count < 2 and return_activity is not true and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        number_of_reopens > 0 and {'gold' 'platinum'} contains status_loyalty and driver_points > 90 and not {'брест' 'лида' 'гродно' 'борисов'} contains city and LoyaltyPointBWithdraw is true and {'en' 'uz'} contains task_language and country = 'uzb' and all_tags contains 'макрос_нет_точки_из_за_фрода_с_авиарежимом' and not all_tags contains 'макрос_нет_точки_из_за_фрода_с_авиарежимом_реопен' and number_of_characters < 850 and not line = 'taxi_logistic_ml'  and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        number_of_reopens > 0 and {'gold' 'platinum'} contains status_loyalty and driver_points > 90 and not {'брест' 'лида' 'гродно' 'борисов'} contains city and LoyaltyPointBWithdraw is true and {'en' 'uz'} contains task_language and country = 'uzb' and all_tags contains 'макрос_нет_точки_из_за_фрода_с_авиарежимом' and not all_tags contains 'макрос_нет_точки_из_за_фрода_с_авиарежимом_реопен' and number_of_characters < 850 and not line = 'taxi_logistic_ml'  and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        (activity_decrease = 0 or (driver_activity_return_count > 1 and (cancel_distance_raw > 100 or order_status != 'cancelled/waiting') and not order_comment is undefined )) and (support_taxi_driver_allow_promo is not false or driver_promocodes_count > 0 or cancel_distance_raw > 100 or not {'finished/cancelled' 'cancelled/waiting'} contains order_status ) and number_of_reopens = 0 and success_order_flg is false and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        cancel_time_raw < 600 and number_of_reopens = 0 and driver_arrived is true and payment_decisions is false and payment_type != 'cash' and {'finished/cancelled' 'finished/failed'} contains order_status and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        cancel_time_raw < 600 and number_of_reopens = 0 and driver_arrived is true and payment_decisions is false and payment_type != 'cash' and {'finished/cancelled' 'finished/failed'} contains order_status and {'en' 'uz'} contains task_language and country = 'uzb' and number_of_characters < 850 and not line = 'taxi_logistic_ml' and country != 'arm' and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined ) and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
        """,
        """
        final_ride_duration < 1 and success_order_flg is true and payment_type != 'cash' and payment_decisions is false and {'econom' 'start' 'vezeteconom' 'vezetbusiness'  'business' 'comfortplus' 'uberx' 'uberselect' 'uberselectplus' 'ubernight'} contains tariff and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        """,
        """
        driver_points < 10 and not line = 'taxi_davos_parks_new'
        """,
        """
        cancel_time_raw < 600 and not final_transaction_status = 'hold_fail' and driver_arrived is true and payment_decisions is false and payment_type != 'cash' and {'finished/cancelled' 'finished/failed'} contains order_status and (country != 'fin' and country != 'rou' and country != 'mda') and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        """,
        """
        cancel_time_raw < 600 and not final_transaction_status = 'hold_fail' and driver_arrived is true and payment_decisions is false and payment_type != 'cash' and {'finished/cancelled' 'finished/failed'} contains order_status and (country != 'fin' and country != 'rou' and country != 'mda') and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        """,
        """
        cancel_time_raw < 600 and not final_transaction_status = 'hold_fail' and driver_arrived is true and payment_decisions is false and payment_type != 'cash' and {'finished/cancelled' 'finished/failed'} contains order_status and (country != 'fin' and country != 'rou' and country != 'mda') and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        """,
        """
        cancel_distance_raw > 300 and driver_arrived is true and payment_decisions is false and payment_type != 'cash' and {'finished/cancelled' 'finished/failed'} contains order_status and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        """,
        """
        cancel_distance_raw > 300 and driver_arrived is true and payment_decisions is false and payment_type != 'cash' and {'finished/cancelled' 'finished/failed'} contains order_status and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        """,
        """
        cancel_distance_raw > 300 and driver_arrived is true and payment_decisions is false and payment_type != 'cash' and {'finished/cancelled' 'finished/failed'} contains order_status and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
        """,
    ],
)
async def test_smoke_large(predicate_rule):
    pypred_predicate = pypred.Predicate(predicate_rule)
    lark_predicate = predicate.Predicate(predicate_rule)

    pypred_result = pypred_predicate.evaluate({})
    lark_result = lark_predicate.evaluate({})

    assert pypred_result is False
    assert bool(lark_result) is False
    assert pypred_result == bool(lark_result)


@pytest.mark.parametrize(
    'predicate_rule',
    [
        """
    number_of_reopens = 0
    and {'gold' 'platinum'} contains status_loyalty
    and driver_points > 90
    and not {'брест' 'лида' 'гродно' 'борисов'} contains city
    and (LoyaltyPointBWithdraw is false or LoyaltyPointBWithdraw is undefined )
    and (device_model contains 'iPhone' or device_model contains 'iPad' or device_model contains 'IPHONE')
    and {'rus' 'blr' 'kaz' 'kgz'} contains country
    and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
    and number_of_characters < 850
    and not line = 'taxi_logistic_ml'
    and (support_oasis_no_ml is false or support_oasis_no_ml is undefined )
    and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined )
    and not comment_lowercased contains ' ID '
    and not comment_lowercased contains ' цели '
    and not comment_lowercased contains ' чат '
    and not comment_lowercased contains 'qr код'
    and not comment_lowercased contains 'qrкод'
    and not comment_lowercased contains 'tap2go'
    and not comment_lowercased contains 'авиарежим'
    and not comment_lowercased contains 'активн'
    and not comment_lowercased contains 'атмините заказ'
    and not comment_lowercased contains 'балл'
    and not comment_lowercased contains 'без звук'
    and not comment_lowercased contains 'без коэф'
    and not comment_lowercased contains 'бронз'
    and not comment_lowercased contains 'был +'
    and not comment_lowercased contains 'был на месте'
    and not comment_lowercased contains 'был не на линии'
    and not comment_lowercased contains 'было +'
    and not comment_lowercased contains 'в другой район'
    and not comment_lowercased contains 'в другой стороне'
    and not comment_lowercased contains 'в другую сторону'
    and not comment_lowercased contains 'в итоге ехал'
    and not comment_lowercased contains 'в определенном районе'
    and not comment_lowercased contains 'в поддержку с просьбой'
    and not comment_lowercased contains 'в противоположную сторону'
    and not comment_lowercased contains 'в туалет'
    and not comment_lowercased contains 'ведёт неправильно'
    and not comment_lowercased contains 'включал выключал'
    and not comment_lowercased contains 'включить ожидание'
    and not comment_lowercased contains 'возврат отдал'
    and not comment_lowercased contains 'возврат я отдал'
    and not comment_lowercased contains 'вопрос не решен'
    and not comment_lowercased contains 'вопрос не решён'
    and not comment_lowercased contains 'времени в пути'
    and not comment_lowercased contains 'время в пути'
    and not comment_lowercased contains 'вручил посылку'
    and not comment_lowercased contains 'все перезапустил'
    and not comment_lowercased contains 'всё перезапустил'
    and not comment_lowercased contains 'все сделал'
    and not comment_lowercased contains 'всё сделал'
    and not comment_lowercased contains 'встроенного навиг'
    and not comment_lowercased contains 'встроенной навиг'
    and not comment_lowercased contains 'встроенную навиг'
    and not comment_lowercased contains 'вторую точку не показывает'
    and not comment_lowercased contains 'вы даёте мне'
    and not comment_lowercased contains 'вы меня отправили'
    and not comment_lowercased contains 'выбранный район'
    and not comment_lowercased contains 'выехать с территории'
    and not comment_lowercased contains 'выключенным приложением'
    and not comment_lowercased contains 'выплата отобразится'
    and not comment_lowercased contains 'высокий спрос'
    and not comment_lowercased contains 'высокого спроса'
    and not comment_lowercased contains 'выходил с линии'
    and not comment_lowercased contains 'выходить на связь'
    and not comment_lowercased contains 'выхожу с линии'
    and not comment_lowercased contains 'вышел с приложения'
    and not comment_lowercased contains 'гибкий'
    and not comment_lowercased contains 'главный вход'
    and not comment_lowercased contains 'груз забрал'
    and not comment_lowercased contains 'грузчик'
    and not comment_lowercased contains 'даете далеко'
    and not comment_lowercased contains 'даёте дальние'
    and not comment_lowercased contains 'даете заказ'
    and not comment_lowercased contains 'даёте заказ'
    and not comment_lowercased contains 'дали мне заказ'
    and not comment_lowercased contains 'дамой'
    and not comment_lowercased contains 'дачные участки'
    and not comment_lowercased contains 'дают заказы'
    and not comment_lowercased contains 'диспетчер'
    and not comment_lowercased contains 'для приглашения'
    and not comment_lowercased contains 'дней с заказами'
    and not comment_lowercased contains 'до меня дозвониться'
    and not comment_lowercased contains 'долгая поездка'
    and not comment_lowercased contains 'долго проходит'
    and not comment_lowercased contains 'домой'
    and not comment_lowercased contains 'доступ ограничен'
    and not comment_lowercased contains 'еду с пассажиром'
    and not comment_lowercased contains 'ехал больше'
    and not comment_lowercased contains 'ехал дольше'
    and not comment_lowercased contains 'ждать следующего заказа'
    and not comment_lowercased contains 'за время'
    and not comment_lowercased contains 'заблокировали'
    and not comment_lowercased contains 'заводится'
    and not comment_lowercased contains 'заводиться'
    and not comment_lowercased contains 'заказ выполнил'
    and not comment_lowercased contains 'заказ даете'
    and not comment_lowercased contains 'заказ даёте'
    and not comment_lowercased contains 'заказ дали'
    and not comment_lowercased contains 'заказ не корректно'
    and not comment_lowercased contains 'заказ не приближает'
    and not comment_lowercased contains 'заказ не устраивает'
    and not comment_lowercased contains 'заказ стоил'
    and not comment_lowercased contains 'заказ стоит'
    and not comment_lowercased contains 'заказы не устраивают'
    and not comment_lowercased contains 'закачал заново'
    and not comment_lowercased contains 'заново скачал'
    and not comment_lowercased contains 'занят'
    and not comment_lowercased contains 'заправк'
    and not comment_lowercased contains 'золот'
    and not comment_lowercased contains 'зоне повышенного'
    and not comment_lowercased contains 'идентификацию личности'
    and not comment_lowercased contains 'идентификация личности'
    and not comment_lowercased contains 'идет проверка'
    and not comment_lowercased contains 'из-за пробок'
    and not comment_lowercased contains 'изменить вид оплаты'
    and not comment_lowercased contains 'инструктаж'
    and not comment_lowercased contains 'исправьте'
    and not comment_lowercased contains 'как вы распределяе'
    and not comment_lowercased contains 'как подключить'
    and not comment_lowercased contains 'как работает'
    and not comment_lowercased contains 'как я могу посмотреть'
    and not comment_lowercased contains 'кис арт'
    and not comment_lowercased contains 'км от меня'
    and not comment_lowercased contains 'км. от меня'
    and not comment_lowercased contains 'когда исправят'
    and not comment_lowercased contains 'компенс'
    and not comment_lowercased contains 'конечную точку'
    and not comment_lowercased contains 'конечный адрес'
    and not comment_lowercased contains 'кэш очисти'
    and not comment_lowercased contains 'кэш почисти'
    and not comment_lowercased contains 'кэш почищен'
    and not comment_lowercased contains 'кэш приложения'
    and not comment_lowercased contains 'кэш чистил'
    and not comment_lowercased contains 'лимит переключений'
    and not comment_lowercased contains 'мне дозвониться'
    and not comment_lowercased contains 'мне другой заказ'
    and not comment_lowercased contains 'моем налоге'
    and not comment_lowercased contains 'моем районе'
    and not comment_lowercased contains 'мои налоги'
    and not comment_lowercased contains 'мой налог'
    and not comment_lowercased contains 'мой район'
    and not comment_lowercased contains 'на безналичн'
    and not comment_lowercased contains 'на другой адрес'
    and not comment_lowercased contains 'на лечении'
    and not comment_lowercased contains 'на линии не был'
    and not comment_lowercased contains 'на скриншоте'
    and not comment_lowercased contains 'на экране не было'
    and not comment_lowercased contains 'навигатор привел'
    and not comment_lowercased contains 'навигатор привёл'
    and not comment_lowercased contains 'навигатор привёл'
    and not comment_lowercased contains 'назначили заказ'
    and not comment_lowercased contains 'настроить приложение'
    and not comment_lowercased contains 'находился в режиме'
    and not comment_lowercased contains 'нахожусь в другом'
    and not comment_lowercased contains 'не был на линии'
    and not comment_lowercased contains 'не было интернета'
    and not comment_lowercased contains 'не было на линии'
    and not comment_lowercased contains 'не в сторону'
    and not comment_lowercased contains 'не в ту сторону'
    and not comment_lowercased contains 'не вижу точку'
    and not comment_lowercased contains 'не включается на месте'
    and not comment_lowercased contains 'не выходит на связь'
    and not comment_lowercased contains 'не даёт в ту сторону'
    and not comment_lowercased contains 'не доступна опция'
    and not comment_lowercased contains 'не доступна функция'
    and not comment_lowercased contains 'не меняется форма'
    and not comment_lowercased contains 'не могу выполнить'
    and not comment_lowercased contains 'не могу завершить'
    and not comment_lowercased contains 'не могу изменить способ'
    and not comment_lowercased contains 'не могу изменить статус'
    and not comment_lowercased contains 'не могу нажать'
    and not comment_lowercased contains 'не могу отметится'
    and not comment_lowercased contains 'не могу отметиться'
    and not comment_lowercased contains 'не могу поставить'
    and not comment_lowercased contains 'не могу прислать скрин'
    and not comment_lowercased contains 'не на линии '
    and not comment_lowercased contains 'не обновился уровень'
    and not comment_lowercased contains 'не по пути'
    and not comment_lowercased contains 'не показываются коэф'
    and not comment_lowercased contains 'не получается сменить'
    and not comment_lowercased contains 'не попути'
    and not comment_lowercased contains 'не успеваю поставить статус'
    and not comment_lowercased contains 'не шлите заявки'
    and not comment_lowercased contains 'неверный адрес'
    and not comment_lowercased contains 'недоступна опция'
    and not comment_lowercased contains 'недоступна функция'
    and not comment_lowercased contains 'нельзя проехать'
    and not comment_lowercased contains 'неправильно считает'
    and not comment_lowercased contains 'ни разу не просил'
    and not comment_lowercased contains 'низился приоритет'
    and not comment_lowercased contains 'ничего не изменилось'
    and not comment_lowercased contains 'нович'
    and not comment_lowercased contains 'нужна связ'
    and not comment_lowercased contains 'нужно связ'
    and not comment_lowercased contains 'нужно чуть больше'
    and not comment_lowercased contains 'обратно за свой'
    and not comment_lowercased contains 'обратно пуст'
    and not comment_lowercased contains 'ограничен доступ'
    and not comment_lowercased contains 'ожидание было'
    and not comment_lowercased contains 'оператор'
    and not comment_lowercased contains 'опоздание'
    and not comment_lowercased contains 'опция недоступна'
    and not comment_lowercased contains 'отдал заказ'
    and not comment_lowercased contains 'отдал посылку'
    and not comment_lowercased contains 'отдельное приложение'
    and not comment_lowercased contains 'отдельном приложении'
    and not comment_lowercased contains 'отложен'
    and not comment_lowercased contains 'отмените заказ'
    and not comment_lowercased contains 'отмените пожалуйста'
    and not comment_lowercased contains 'отмените этот заказ'
    and not comment_lowercased contains 'отправител'
    and not comment_lowercased contains 'отправитель'
    and not comment_lowercased contains 'отчистил кэш'
    and not comment_lowercased contains 'очеред'
    and not comment_lowercased contains 'очистил кэш'
    and not comment_lowercased contains 'очистка кэш'
    and not comment_lowercased contains 'памяти достаточно'
    and not comment_lowercased contains 'переводит на налич'
    and not comment_lowercased contains 'перезагружал'
    and not comment_lowercased contains 'перезагрузил'
    and not comment_lowercased contains 'перезагрузить'
    and not comment_lowercased contains 'перезагрузка не помог'
    and not comment_lowercased contains 'перезашел в приложение'
    and not comment_lowercased contains 'переити на безнал'
    and not comment_lowercased contains 'переити на нал'
    and not comment_lowercased contains 'перейти на безнал'
    and not comment_lowercased contains 'перейти на нал'
    and not comment_lowercased contains 'переключает на налич'
    and not comment_lowercased contains 'переключением безнал'
    and not comment_lowercased contains 'переключением нал'
    and not comment_lowercased contains 'переключить форму оплаты'
    and not comment_lowercased contains 'перекрыт'
    and not comment_lowercased contains 'перекусить'
    and not comment_lowercased contains 'перерасчет'
    and not comment_lowercased contains 'перерасчёт'
    and not comment_lowercased contains 'переустанавлива'
    and not comment_lowercased contains 'переустановил'
    and not comment_lowercased contains 'переустановлено'
    and not comment_lowercased contains 'переустоновил'
    and not comment_lowercased contains 'платин'
    and not comment_lowercased contains 'платного ожидания'
    and not comment_lowercased contains 'платном ожидании'
    and not comment_lowercased contains 'плохая дорог'
    and not comment_lowercased contains 'плохие дороги'
    and not comment_lowercased contains 'плохой дорог'
    and not comment_lowercased contains 'по делам'
    and not comment_lowercased contains 'по пути'
    and not comment_lowercased contains 'по факту ехал'
    and not comment_lowercased contains 'повышающего коэф'
    and not comment_lowercased contains 'повышенного спроса'
    and not comment_lowercased contains 'подаёте'
    and not comment_lowercased contains 'подач'
    and not comment_lowercased contains 'поделам'
    and not comment_lowercased contains 'подмен'
    and not comment_lowercased contains 'поездки без пасажиров'
    and not comment_lowercased contains 'поездки не учитываются'
    and not comment_lowercased contains 'показывает проезд'
    and not comment_lowercased contains 'получател'
    and not comment_lowercased contains 'поменять оплату'
    and not comment_lowercased contains 'после прожатия'
    and not comment_lowercased contains 'поставьте статус'
    and not comment_lowercased contains 'посылка доставлен'
    and not comment_lowercased contains 'посылку забрал'
    and not comment_lowercased contains 'почистил кэш'
    and not comment_lowercased contains 'превышен лемит'
    and not comment_lowercased contains 'привел навигатор'
    and not comment_lowercased contains 'привёл навигатор'
    and not comment_lowercased contains 'приложение переустан'
    and not comment_lowercased contains 'приложение удал'
    and not comment_lowercased contains 'приходится перезагру'
    and not comment_lowercased contains 'пришел второй раз'
    and not comment_lowercased contains 'пришёл второй раз'
    and not comment_lowercased contains 'пришел когда нажимал'
    and not comment_lowercased contains 'пришёл повторно'
    and not comment_lowercased contains 'пришлось перезагру'
    and not comment_lowercased contains 'пробил колесо'
    and not comment_lowercased contains 'проблемы с машиной'
    and not comment_lowercased contains 'проверить мой аккаунт'
    and not comment_lowercased contains 'проверка личност'
    and not comment_lowercased contains 'проверка личности'
    and not comment_lowercased contains 'проверку личности'
    and not comment_lowercased contains 'проверять личность'
    and not comment_lowercased contains 'программа не пересчитала '
    and not comment_lowercased contains 'продолжают назначаться'
    and not comment_lowercased contains 'проезда нет'
    and not comment_lowercased contains 'пройти тест'
    and not comment_lowercased contains 'пром код'
    and not comment_lowercased contains 'промакод'
    and not comment_lowercased contains 'промкод'
    and not comment_lowercased contains 'промо код'
    and not comment_lowercased contains 'промокод'
    and not comment_lowercased contains 'промо-код'
    and not comment_lowercased contains 'просили скрин'
    and not comment_lowercased contains 'просили фото'
    and not comment_lowercased contains 'противоположную сторону'
    and not comment_lowercased contains 'проходила проверка'
    and not comment_lowercased contains 'прошел тестирование'
    and not comment_lowercased contains 'прошёл тестирование'
    and not comment_lowercased contains 'прошу сменить статус'
    and not comment_lowercased contains 'разворачиваться'
    and not comment_lowercased contains 'распределяет заказы'
    and not comment_lowercased contains 'ремни на месте'
    and not comment_lowercased contains 'с безнала на нал'
    and not comment_lowercased contains 'с гарантиями'
    and not comment_lowercased contains 'с повышенным спросом'
    and not comment_lowercased contains 'с проводник'
    and not comment_lowercased contains 'самолёт не включал'
    and not comment_lowercased contains 'свяжитесь пожалуйста'
    and not comment_lowercased contains 'сделал то что вы сказали'
    and not comment_lowercased contains 'сделал эти пункты'
    and not comment_lowercased contains 'сделать скрин'
    and not comment_lowercased contains 'сегодня один раз'
    and not comment_lowercased contains 'серебр'
    and not comment_lowercased contains 'сколько раз в день'
    and not comment_lowercased contains 'слот'
    and not comment_lowercased contains 'случайно нажал'
    and not comment_lowercased contains 'смена'
    and not comment_lowercased contains 'смену'
    and not comment_lowercased contains 'смены'
    and not comment_lowercased contains 'смотрите скриншот'
    and not comment_lowercased contains 'снизили приоритет'
    and not comment_lowercased contains 'снимите заказ'
    and not comment_lowercased contains 'снимите пожалуйста заказ'
    and not comment_lowercased contains 'снимите с меня'
    and not comment_lowercased contains 'снимите текущий заказ'
    and not comment_lowercased contains 'снт '
    and not comment_lowercased contains 'снялся с линии'
    and not comment_lowercased contains 'снят с линии'
    and not comment_lowercased contains 'сошёл с линии'
    and not comment_lowercased contains 'сошел с линии '
    and not comment_lowercased contains 'способ оплаты'
    and not comment_lowercased contains 'стандартные процедуры'
    and not comment_lowercased contains 'стер приложение'
    and not comment_lowercased contains 'стёр приложение'
    and not comment_lowercased contains 'сторону дома'
    and not comment_lowercased contains 'стоял на месте'
    and not comment_lowercased contains 'таксометр выключен'
    and not comment_lowercased contains 'термо'
    and not comment_lowercased contains 'товар доставлен'
    and not comment_lowercased contains 'только безнал'
    and not comment_lowercased contains 'только вышел'
    and not comment_lowercased contains 'только наличные'
    and not comment_lowercased contains 'только что вышел'
    and not comment_lowercased contains 'точки б'
    and not comment_lowercased contains 'точки конечн'
    and not comment_lowercased contains 'точку б'
    and not comment_lowercased contains 'тупик'
    and not comment_lowercased contains 'удалил приложение'
    and not comment_lowercased contains 'удалял скачивал'
    and not comment_lowercased contains 'ужасные дороги'
    and not comment_lowercased contains 'указал дорогу'
    and not comment_lowercased contains 'усталост'
    and not comment_lowercased contains 'установил лимит'
    and not comment_lowercased contains 'установил снова'
    and not comment_lowercased contains 'уходишь с линии'
    and not comment_lowercased contains 'ухожу с линии'
    and not comment_lowercased contains 'ушел с линии'
    and not comment_lowercased contains 'ушёл с линии'
    and not comment_lowercased contains 'фактическое время'
    and not comment_lowercased contains 'фотоконтроль'
    and not comment_lowercased contains 'функция недоступна'
    and not comment_lowercased contains 'цель'
    and not comment_lowercased contains 'чем было заявлено'
    and not comment_lowercased contains 'через закрытую дорогу'
    and not comment_lowercased contains 'чистил кэш'
    and not comment_lowercased contains 'что долго работаю'
    and not comment_lowercased contains 'чтобы заявки не приходили'
    and not comment_lowercased contains 'энергосбережен'
    and not comment_lowercased contains 'юрист'
    and not comment_lowercased contains 'обещал'
    and not comment_lowercased contains 'постоян'
    and not comment_lowercased contains ' лини'
    and not comment_lowercased contains ' лини'
    and not comment_lowercased contains 'свобод'
    and not comment_lowercased contains 'машин нет'
    and not comment_lowercased contains ' км '
    and not comment_lowercased contains 'рядом'
    and not comment_lowercased contains 'далек'
    and not comment_lowercased contains 'налич'
    and not comment_lowercased contains 'карта'
    and not comment_lowercased contains 'не дает'
    and not comment_lowercased contains 'звук'
    and not comment_lowercased contains 'ушел'
    and not comment_lowercased contains 'сошел' and not {'functional_driver_moderation' 'logistic_drivers_2_level' 'taxi_logictic_drivers_sort' 'logistic_no_pay' 'logistic_no_pay_reopen' 'taxi_logictic_drivers_selected'} contains line
    """,
        """
    number_of_reopens = 0
    and number_of_characters < 850 and not line = 'taxi_logistic_ml'
    and (task_language = 'ru' or (task_language is undefined and {'rus' 'blr' 'kaz' 'kgz'} contains country))
    and (support_oasis_no_ml is false or support_oasis_no_ml is undefined ) and (support_oasis_no_ml_best_sup is false or support_oasis_no_ml_best_sup is undefined)
    and (((
    comment_lowercased contains 'клиент' or
    comment_lowercased contains 'пасажир' or
    comment_lowercased contains 'пасажыр' or
    comment_lowercased contains 'пасожир' or
    comment_lowercased contains 'пассажир' or
    comment_lowercased contains 'пользовател' or
    comment_lowercased contains 'посажир' or
    comment_lowercased contains 'посожир' or
    comment_lowercased contains 'поссажир')
    and (
    comment_lowercased contains 'атличный' or
    comment_lowercased contains ' благодарность ' or
    comment_lowercased contains ' благодарности' or
    comment_lowercased contains 'благодарен ему' or
    comment_lowercased contains 'ему благодарен' or
    comment_lowercased contains ' вежливый' or
    comment_lowercased contains ' вежливая' or
    comment_lowercased contains 'воспитанный' or
    comment_lowercased contains 'воспитанная' or
    comment_lowercased contains 'добродушный' or
    comment_lowercased contains 'добродушная' or
    comment_lowercased contains 'доброжелательный' or
    comment_lowercased contains 'доброжелательная' or
    comment_lowercased contains ' добропорядочный' or
    comment_lowercased contains ' добропорядочная' or
    comment_lowercased contains ' добросовестный' or
    comment_lowercased contains ' добросовестная' or
    comment_lowercased contains 'идеальный' or
    comment_lowercased contains ' культурный' or
    comment_lowercased contains ' культурная' or
    comment_lowercased contains 'отблагодарить' or
    comment_lowercased contains ' ответственный' or
    comment_lowercased contains ' ответственная' or
    comment_lowercased contains 'отличный' or
    comment_lowercased contains 'офиген' or
    comment_lowercased contains 'очень добрый' or
    comment_lowercased contains 'паблагодарить' or
    comment_lowercased contains 'поблагодарит' or
    comment_lowercased contains 'по благодарит' or
    comment_lowercased contains 'поблогодорит' or
    comment_lowercased contains 'позитивный' or
    comment_lowercased contains 'позитивная' or
    comment_lowercased contains 'положительный отзыв' or
    comment_lowercased contains ' понимающий' or
    comment_lowercased contains ' понимающая' or
    comment_lowercased contains ' порядочный' or
    comment_lowercased contains ' порядочная' or
    comment_lowercased contains 'прекраснейший' or
    comment_lowercased contains 'прекраснейшая' or
    comment_lowercased contains ' приличный' or
    comment_lowercased contains ' приличная' or
    comment_lowercased contains ' приятный' or
    comment_lowercased contains ' приятная' or
    comment_lowercased contains 'самый лучший' or
    comment_lowercased contains 'собеседник' or
    comment_lowercased contains 'супер ' or
    comment_lowercased contains ' честный' or
    comment_lowercased contains ' честная' or
    comment_lowercased contains 'это не жалоба'))
    or (
    comment_lowercased contains 'благадарю за чаевые' or
    comment_lowercased contains 'спасибо большое за чаевые' or
    comment_lowercased contains 'спасибо большое клиенту за чаевые' or
    comment_lowercased contains 'спасибо большое пассажиру за чаевые' or
    comment_lowercased contains 'спасибо за чаевие' or
    comment_lowercased contains 'спасибо за чаевий' or
    comment_lowercased contains 'спасибо за чаевые ' or
    comment_lowercased contains 'спасибо за чай' or
    comment_lowercased contains 'спасибо за чайвы ' or
    comment_lowercased contains 'спасибо за чайвые' or
    comment_lowercased contains 'спасибо за чаыве' or
    comment_lowercased contains 'спасибо клиентке за чаевые' or
    comment_lowercased contains 'спасибо клиенту за чаевые' or
    comment_lowercased contains 'спасибо пассажиру за чаевые' or
    comment_lowercased contains 'спасибо этой клиентке за чаевые' or
    comment_lowercased contains 'спасибо этому клиенту за чаевые' or
    comment_lowercased contains 'спосибо за чаевые ' or
    comment_lowercased contains 'спосибо за чай' or
    comment_lowercased contains 'большие чаевые' or
    comment_lowercased contains 'огромные чаевые' or
    comment_lowercased contains 'щедрые чаевые' or
    comment_lowercased contains 'хорошая она человек' or
    comment_lowercased contains 'хорошие они люди' or
    comment_lowercased contains 'хороший он человек' or
    comment_lowercased contains 'хороший она человек' or
    comment_lowercased contains 'хороший человек' or
    comment_lowercased contains 'добрый человек' or
    comment_lowercased contains 'было побольше таких' or
    comment_lowercased contains 'все были бы такими' or
    comment_lowercased contains 'все такие были' or
    comment_lowercased contains 'всегда бы таких' or
    comment_lowercased contains 'которого я встречал' or
    comment_lowercased contains 'которого я когда либо' or
    comment_lowercased contains 'которого я когда-либо' or
    comment_lowercased contains 'которого я только встречал' or
    comment_lowercased contains 'которых я встречал' or
    comment_lowercased contains 'написать положительный отзыв' or
    comment_lowercased contains 'по больше бы таких' or
    comment_lowercased contains 'побольше б таких' or
    comment_lowercased contains 'побольше бы таких' or
    comment_lowercased contains 'почаще бы таких' or
    comment_lowercased contains 'спасибо за таких клиентов' or
    comment_lowercased contains 'спасибо за таких пассажиров' or
    comment_lowercased contains 'спасибо таким клиентам' or
    comment_lowercased contains 'спасибо таким пассажирам' or
    comment_lowercased contains 'таких клиентов побольше' or
    comment_lowercased contains 'таких пассажиров побольше' or
    comment_lowercased contains 'безумно красивая' or
    comment_lowercased contains 'влюбился в нее' or
    comment_lowercased contains 'влюбился в неё' or
    comment_lowercased contains 'девушка оставила хорошее настроение' or
    comment_lowercased contains 'девушка очень красивая' or
    comment_lowercased contains 'девушка прекрасная' or
    comment_lowercased contains 'забыла свое сердце' or
    comment_lowercased contains 'забыла своё сердце' or
    comment_lowercased contains 'забыла счастье в машине' or
    comment_lowercased contains 'замечательная девушка' or
    comment_lowercased contains 'милый человек' or
    comment_lowercased contains 'мое сердечко ' or
    comment_lowercased contains 'моё сердечко ' or
    comment_lowercased contains 'мое сердце' or
    comment_lowercased contains 'моё сердце' or
    comment_lowercased contains 'моего сердца' or
    comment_lowercased contains 'обаятельная девушка' or
    comment_lowercased contains 'она мне очень понравилась' or
    comment_lowercased contains 'она очень красивая' or
    comment_lowercased contains 'оставил хорошее настроение' or
    comment_lowercased contains 'оставила хорошее настроение' or
    comment_lowercased contains 'очень красивая девушка' or
    comment_lowercased contains 'очень милая девушка' or
    comment_lowercased contains 'очень приятная девушка' or
    comment_lowercased contains 'перлестная девушка' or
    comment_lowercased contains 'понравилась эта девушка' or
    comment_lowercased contains 'самая красивая девушка' or
    comment_lowercased contains 'сердце украла' or
    comment_lowercased contains 'симпатичная девушка' or
    comment_lowercased contains 'симпотичная девушка' or
    comment_lowercased contains 'я влюбился' or
    comment_lowercased contains 'я прям влюбился')
    or
    (comment_lowercased contains 'наоборот'
    and (comment_lowercased contains 'добрые слова'
    or comment_lowercased contains 'вы не так поняли'
    or comment_lowercased contains 'не жалуюсь'
    or comment_lowercased contains 'не пожаловаться'
    or comment_lowercased contains 'поблагодарить'
    or comment_lowercased contains 'похвалил'))
    or
    (comment_lowercased contains 'не жалоба'
    and (comment_lowercased contains 'благодарность'
    or comment_lowercased contains 'комплимент'
    or comment_lowercased contains 'наоборот'))
    or
    (comment_lowercased contains 'вы не поняли'
    and comment_lowercased contains 'хороший')
    or (
    (comment_lowercased contains 'лучший клиент' and
    number_of_characters < 17) or
    (comment_lowercased contains 'лучший пассажир' and
    number_of_characters < 19) or
    (comment_lowercased contains 'очень хорошие клиенты' and
    number_of_characters < 25) or
    (comment_lowercased contains 'очень хорошие пассажиры' and
    number_of_characters < 27) or
    (comment_lowercased contains 'очень хороший клиент' and
    number_of_characters < 24) or
    (comment_lowercased contains 'очень хороший пассажир' and
    number_of_characters < 26) or
    (comment_lowercased contains 'хорошие клиенты' and
    number_of_characters < 19) or
    (comment_lowercased contains 'хороший клиент' and
    number_of_characters < 18) or
    (comment_lowercased contains 'хороший пассажир' and
    number_of_characters < 20) or
    (comment_lowercased contains 'клиент хороший' and
    number_of_characters < 18) or
    (comment_lowercased contains 'пассажир хороший' and
    number_of_characters < 20) or
    (comment_lowercased contains 'пассажиры хорошие' and
    number_of_characters < 21) or
    (comment_lowercased contains 'клиенты хорошие' and
    number_of_characters < 19) or
    (comment_lowercased contains 'классный пассажир' and
    number_of_characters < 21) or
    (comment_lowercased contains 'классный клиент' and
    number_of_characters < 19) or
    (comment_lowercased contains 'пассажир классный' and
    number_of_characters < 21) or
    (comment_lowercased contains 'клиент классный' and
    number_of_characters < 19)))
    and not comment_lowercased contains 'неблагодар'
    and not comment_lowercased contains 'не благодар'
    and not comment_lowercased contains 'невежлив'
    and not comment_lowercased contains 'не вежлив'
    and not comment_lowercased contains 'невоспитан'
    and not comment_lowercased contains 'не воспитан'
    and not comment_lowercased contains 'не добропорядочн'
    and not comment_lowercased contains 'не добросовестн'
    and not comment_lowercased contains 'недобропорядочн'
    and not comment_lowercased contains 'недобросовестн'
    and not comment_lowercased contains 'некультурн'
    and not comment_lowercased contains 'не культурн'
    and not comment_lowercased contains 'неответствен'
    and not comment_lowercased contains 'не ответствен'
    and not comment_lowercased contains 'непонимающ'
    and not comment_lowercased contains 'не понимающ'
    and not comment_lowercased contains 'не порядочн'
    and not comment_lowercased contains 'непорядочн'
    and not comment_lowercased contains 'не приличн'
    and not comment_lowercased contains 'не приятн'
    and not comment_lowercased contains 'неприличн'
    and not comment_lowercased contains 'неприятн'
    and not comment_lowercased contains 'нечестн'
    and not comment_lowercased contains 'не честн'
    and not comment_lowercased contains 'не хорош'
    and not comment_lowercased contains 'нехорош'
    and not comment_lowercased contains 'не доброжелател'
    and not comment_lowercased contains 'недоброжелател'
    and not comment_lowercased contains 'не очень вежлив'
    and not comment_lowercased contains 'не очень воспитан'
    and not comment_lowercased contains 'не очень доброжелательн'
    and not comment_lowercased contains 'не очень добропорядочн'
    and not comment_lowercased contains 'не очень добросовестн'
    and not comment_lowercased contains 'не очень культурн'
    and not comment_lowercased contains 'не очень ответствен'
    and not comment_lowercased contains 'не очень понимающ'
    and not comment_lowercased contains 'не очень порядочн'
    and not comment_lowercased contains 'не очень приличн'
    and not comment_lowercased contains 'не очень приятн'
    and not comment_lowercased contains 'не очень честн'
    and not comment_lowercased contains 'не особо вежлив'
    and not comment_lowercased contains 'не особо воспитан'
    and not comment_lowercased contains 'не особо культурн'
    and not comment_lowercased contains 'не особо понимающ'
    and not comment_lowercased contains 'не особо порядочн'
    and not comment_lowercased contains 'не особо приличн'
    and not comment_lowercased contains 'не особо приятн'
    and not comment_lowercased contains 'не особо честн'
    and not comment_lowercased contains 'неособо вежлив'
    and not comment_lowercased contains 'неособо воспитан'
    and not comment_lowercased contains 'неособо культурн'
    and not comment_lowercased contains 'неособо понимающ'
    and not comment_lowercased contains 'неособо порядочн'
    and not comment_lowercased contains 'неособо приличн'
    and not comment_lowercased contains 'неособо приятн'
    and not comment_lowercased contains 'неособо честн'
    and not comment_lowercased contains 'не самый лучший '
    and not comment_lowercased contains 'не особо добр'
    and not comment_lowercased contains 'не особо хорош'
    and not comment_lowercased contains 'не очень добр'
    and not comment_lowercased contains 'не очень хорош'
    and not comment_lowercased contains 'не самый добр'
    and not comment_lowercased contains 'неособо добр'
    and not comment_lowercased contains 'неособо хорош'
    and not comment_lowercased contains 'не очень собеседник'
    and not comment_lowercased contains 'без культурн'
    and not comment_lowercased contains 'без ответствен'
    and not comment_lowercased contains 'без честн'
    and not comment_lowercased contains 'безкультурн'
    and not comment_lowercased contains 'безответствен'
    and not comment_lowercased contains 'безчестн'
    and not comment_lowercased contains 'бес культурн'
    and not comment_lowercased contains 'бес ответствен'
    and not comment_lowercased contains 'бес честн'
    and not comment_lowercased contains 'бескультурн'
    and not comment_lowercased contains 'бесответствен'
    and not comment_lowercased contains 'бесчестн'
    and not comment_lowercased contains 'без воспитан'
    and not comment_lowercased contains 'безвоспитан'
    and not comment_lowercased contains ' я вежлив'
    and not comment_lowercased contains ' я воспитан'
    and not comment_lowercased contains ' я всегда вежлив'
    and not comment_lowercased contains ' я всегда воспитан'
    and not comment_lowercased contains ' я всегда доброжелательн'
    and not comment_lowercased contains ' я всегда добропорядочн'
    and not comment_lowercased contains ' я всегда добросовестн'
    and not comment_lowercased contains ' я всегда культурн'
    and not comment_lowercased contains ' я всегда ответствен'
    and not comment_lowercased contains ' я всегда порядочн'
    and not comment_lowercased contains ' я всегда приличн'
    and not comment_lowercased contains ' я всегда приятн'
    and not comment_lowercased contains ' я всегда честн'
    and not comment_lowercased contains ' я доброжелательн'
    and not comment_lowercased contains ' я добропорядочн'
    and not comment_lowercased contains ' я добросовестн'
    and not comment_lowercased contains ' я культурн'
    and not comment_lowercased contains ' я ответствен'
    and not comment_lowercased contains ' я отличный '
    and not comment_lowercased contains ' я понимающ'
    and not comment_lowercased contains ' я порядочн'
    and not comment_lowercased contains ' я приличн'
    and not comment_lowercased contains ' я приятн'
    and not comment_lowercased contains ' я сам вежлив'
    and not comment_lowercased contains ' я сам воспитан'
    and not comment_lowercased contains ' я сам доброжелательн'
    and not comment_lowercased contains ' я сам добропорядочн'
    and not comment_lowercased contains ' я сам добросовестн'
    and not comment_lowercased contains ' я сам культурн'
    and not comment_lowercased contains ' я сам ответствен'
    and not comment_lowercased contains ' я сам понимающ'
    and not comment_lowercased contains ' я сам порядочн'
    and not comment_lowercased contains ' я сам приличн'
    and not comment_lowercased contains ' я сам приятн'
    and not comment_lowercased contains ' я сам хороший человек'
    and not comment_lowercased contains ' я сам честн'
    and not comment_lowercased contains ' я со всеми вежлив'
    and not comment_lowercased contains ' я со всеми честн'
    and not comment_lowercased contains ' я хороший человек'
    and not comment_lowercased contains ' я честн'
    and not comment_lowercased contains 'сам я вежлив'
    and not comment_lowercased contains 'сам я воспитан'
    and not comment_lowercased contains 'сам я доброжелательн'
    and not comment_lowercased contains 'сам я добропорядочн'
    and not comment_lowercased contains 'сам я добросовестн'
    and not comment_lowercased contains 'сам я культурн'
    and not comment_lowercased contains 'сам я ответствен'
    and not comment_lowercased contains 'сам я понимающ'
    and not comment_lowercased contains 'сам я порядочн'
    and not comment_lowercased contains 'сам я приличн'
    and not comment_lowercased contains 'сам я приятн'
    and not comment_lowercased contains 'сам я хороший человек'
    and not comment_lowercased contains 'сам я честн'
    and not comment_lowercased contains ' я как вежлив'
    and not comment_lowercased contains ' я как воспитан'
    and not comment_lowercased contains ' я как доброжелательн'
    and not comment_lowercased contains ' я как добропорядочн'
    and not comment_lowercased contains ' я как добросовестн'
    and not comment_lowercased contains ' я как культурн'
    and not comment_lowercased contains ' я как ответствен'
    and not comment_lowercased contains ' я как понимающ'
    and not comment_lowercased contains ' я как порядочн'
    and not comment_lowercased contains ' я как приличн'
    and not comment_lowercased contains ' я как приятн'
    and not comment_lowercased contains ' я как хороший человек'
    and not comment_lowercased contains ' я как честн'
    and not comment_lowercased contains 'благодарности никакой'
    and not comment_lowercased contains 'благодарности ноль'
    and not comment_lowercased contains 'вежливый отказ'
    and not comment_lowercased contains 'виду воспитанная'
    and not comment_lowercased contains 'виду воспитанный'
    and not comment_lowercased contains 'вместо благодарности'
    and not comment_lowercased contains 'где благодарность'
    and not comment_lowercased contains 'день идеальный'
    and not comment_lowercased contains 'день отличный'
    and not comment_lowercased contains 'запах приятный'
    and not comment_lowercased contains 'идеальный водитель'
    and not comment_lowercased contains 'идеальный возможность'
    and not comment_lowercased contains 'идеальный день'
    and not comment_lowercased contains 'идеальный ответ'
    and not comment_lowercased contains 'идеальный план'
    and not comment_lowercased contains 'идеальный повод'
    and not comment_lowercased contains 'идеальный сервис'
    and not comment_lowercased contains 'идеальный способ'
    and not comment_lowercased contains 'культурный ответ'
    and not comment_lowercased contains 'культурный отказ'
    and not comment_lowercased contains 'не думал благодарить'
    and not comment_lowercased contains 'не пытался благодарить'
    and not comment_lowercased contains 'не старался благодарить'
    and not comment_lowercased contains 'никакой благодарности'
    and not comment_lowercased contains 'никакой собеседник'
    and not comment_lowercased contains 'ноль благодарности'
    and not comment_lowercased contains 'одежда приличная'
    and not comment_lowercased contains 'ответ культурный'
    and not comment_lowercased contains 'ответ отличный'
    and not comment_lowercased contains 'отличный день'
    and not comment_lowercased contains 'отличный от '
    and not comment_lowercased contains 'отличный ответ'
    and not comment_lowercased contains 'отличный план'
    and not comment_lowercased contains 'отличный повод'
    and not comment_lowercased contains 'отличный результат'
    and not comment_lowercased contains 'отличный сервис'
    and not comment_lowercased contains 'отличный способ'
    and not comment_lowercased contains 'отличный ход'
    and not comment_lowercased contains 'план отличный'
    and not comment_lowercased contains 'плохо понимающая'
    and not comment_lowercased contains 'плохо понимающий'
    and not comment_lowercased contains 'плохой собеседник'
    and not comment_lowercased contains 'повод отличный'
    and not comment_lowercased contains 'прекраснейшая возможность'
    and not comment_lowercased contains 'прекраснейший день'
    and not comment_lowercased contains 'прекраснейший ответ'
    and not comment_lowercased contains 'прекраснейший способ'
    and not comment_lowercased contains 'приличная одежда'
    and not comment_lowercased contains 'приличная разница'
    and not comment_lowercased contains 'приличная сумма'
    and not comment_lowercased contains 'приличный заработок'
    and not comment_lowercased contains 'приличный километр'
    and not comment_lowercased contains 'приличный костюм'
    and not comment_lowercased contains 'приличный ответ'
    and not comment_lowercased contains 'приличный отказ'
    and not comment_lowercased contains 'приличный путь'
    and not comment_lowercased contains 'приложение супер '
    and not comment_lowercased contains 'приятный запах'
    and not comment_lowercased contains 'программа супер '
    and not comment_lowercased contains 'разница приличная'
    and not comment_lowercased contains 'результат отличный'
    and not comment_lowercased contains 'роде воспитанная'
    and not comment_lowercased contains 'роде воспитанный'
    and not comment_lowercased contains 'самый лучший день'
    and not comment_lowercased contains 'самый лучший сервис'
    and not comment_lowercased contains 'самый лучший способ'
    and not comment_lowercased contains 'сервис отличный'
    and not comment_lowercased contains 'сервис супер'
    and not comment_lowercased contains 'собеседник не очень'
    and not comment_lowercased contains 'собеседник плохой'
    and not comment_lowercased contains 'собеседник так себе'
    and not comment_lowercased contains 'сумма приличная'
    and not comment_lowercased contains 'супер быстро'
    and not comment_lowercased contains 'супер приложение'
    and not comment_lowercased contains 'супер программа'
    and not comment_lowercased contains 'супер просто'
    and not comment_lowercased contains 'супер сервис'
    and not comment_lowercased contains 'так себе собеседник'
    and not comment_lowercased contains 'честный ответ'
    and not comment_lowercased contains 'что в благодарность'
    and not comment_lowercased contains 'роде  вежлив'
    and not comment_lowercased contains 'роде  доброжелательн'
    and not comment_lowercased contains 'роде  добропорядочн'
    and not comment_lowercased contains 'роде  добросовестн'
    and not comment_lowercased contains 'роде  культурн'
    and not comment_lowercased contains 'роде  ответствен'
    and not comment_lowercased contains 'роде  понимающ'
    and not comment_lowercased contains 'роде  порядочн'
    and not comment_lowercased contains 'роде  приличн'
    and not comment_lowercased contains 'роде  приятн'
    and not comment_lowercased contains 'роде  честн'
    and not comment_lowercased contains 'виду вежлив'
    and not comment_lowercased contains 'виду доброжелательн'
    and not comment_lowercased contains 'виду добропорядочн'
    and not comment_lowercased contains 'виду добросовестн'
    and not comment_lowercased contains 'виду культурн'
    and not comment_lowercased contains 'виду ответствен'
    and not comment_lowercased contains 'виду понимающ'
    and not comment_lowercased contains 'виду порядочн'
    and not comment_lowercased contains 'виду приличн'
    and not comment_lowercased contains 'виду приятн'
    and not comment_lowercased contains 'виду честн'
    and not comment_lowercased contains ' бал '
    and not comment_lowercased contains ' знак '
    and not comment_lowercased contains ' кинул '
    and not comment_lowercased contains ' км '
    and not comment_lowercased contains ' км.'
    and not comment_lowercased contains ' наруш'
    and not comment_lowercased contains '5 человек'
    and not comment_lowercased contains 'активн'
    and not comment_lowercased contains 'балл'
    and not comment_lowercased contains 'бензин'
    and not comment_lowercased contains 'ваша программа'
    and not comment_lowercased contains 'верните'
    and not comment_lowercased contains 'высадить'
    and not comment_lowercased contains 'детьми'
    and not comment_lowercased contains 'дойти до машины'
    and not comment_lowercased contains 'документ'
    and not comment_lowercased contains 'дорог нет'
    and not comment_lowercased contains 'дороги нет'
    and not comment_lowercased contains 'доставк'
    and not comment_lowercased contains 'другой машине'
    and not comment_lowercased contains 'другом такси'
    and not comment_lowercased contains 'жаловаться'
    and not comment_lowercased contains 'жалуются'
    and not comment_lowercased contains 'заблокир'
    and not comment_lowercased contains 'закрыли доступ'
    and not comment_lowercased contains 'закрыли мне доступ '
    and not comment_lowercased contains 'запах'
    and not comment_lowercased contains 'издева'
    and not comment_lowercased contains 'каеф'
    and not comment_lowercased contains 'камера'
    and not comment_lowercased contains 'кампенс'
    and not comment_lowercased contains 'каэф'
    and not comment_lowercased contains 'километров'
    and not comment_lowercased contains 'коеф'
    and not comment_lowercased contains 'комисс'
    and not comment_lowercased contains 'комментари'
    and not comment_lowercased contains 'компенс'
    and not comment_lowercased contains 'коэф'
    and not comment_lowercased contains 'минут'
    and not comment_lowercased contains 'моей вины'
    and not comment_lowercased contains 'накажите'
    and not comment_lowercased contains 'настроение испортил'
    and not comment_lowercased contains 'настроения нет'
    and not comment_lowercased contains 'не адекват'
    and not comment_lowercased contains 'не было денег'
    and not comment_lowercased contains 'не было оплат'
    and not comment_lowercased contains 'не выгодн'
    and not comment_lowercased contains 'не выходит'
    and not comment_lowercased contains 'не нашёл'
    and not comment_lowercased contains 'не оплат'
    and not comment_lowercased contains 'не отвечает'
    and not comment_lowercased contains 'не перевел'
    and not comment_lowercased contains 'не платят'
    and not comment_lowercased contains 'не учитывать'
    and not comment_lowercased contains 'неадекват'
    and not comment_lowercased contains 'невыгодн'
    and not comment_lowercased contains 'негатив'
    and not comment_lowercased contains 'незаслужен'
    and not comment_lowercased contains 'неправильно указ'
    and not comment_lowercased contains 'несправедливо'
    and not comment_lowercased contains 'объясняйте'
    and not comment_lowercased contains 'оператор'
    and not comment_lowercased contains 'отвратительный'
    and not comment_lowercased contains 'отказался'
    and not comment_lowercased contains 'отказался оплат'
    and not comment_lowercased contains 'отмен'
    and not comment_lowercased contains 'перевести на карту'
    and not comment_lowercased contains 'платил наличными'
    and not comment_lowercased contains 'платила наличными'
    and not comment_lowercased contains 'платной дороге'
    and not comment_lowercased contains 'повышенных тонах'
    and not comment_lowercased contains 'пожаловаться'
    and not comment_lowercased contains 'послык'
    and not comment_lowercased contains 'посчита'
    and not comment_lowercased contains 'претензи'
    and not comment_lowercased contains 'приор'
    and not comment_lowercased contains 'пробки'
    and not comment_lowercased contains 'прошу принять меры'
    and not comment_lowercased contains 'разобраться'
    and not comment_lowercased contains 'рассчита'
    and not comment_lowercased contains 'расценк'
    and not comment_lowercased contains 'ребен'
    and not comment_lowercased contains 'рейтинг'
    and not comment_lowercased contains 'снимите'
    and not comment_lowercased contains 'сняли'
    and not comment_lowercased contains 'тариф'
    and not comment_lowercased contains 'трубку не бер'
    and not comment_lowercased contains 'уйду в '
    and not comment_lowercased contains 'указан неверно'
    and not comment_lowercased contains 'чёрный список'
    and not comment_lowercased contains ' смс '
    and not comment_lowercased contains 'без пассажир'
    and not comment_lowercased contains 'без пассажиров'
    and not comment_lowercased contains 'без пользовател'
    and not comment_lowercased contains 'будто бы я'
    and not comment_lowercased contains 'в другую сторону'
    and not comment_lowercased contains 'веду себя'
    and not comment_lowercased contains 'все это ложь'
    and not comment_lowercased contains 'всё это ложь'
    and not comment_lowercased contains 'всегда виноват водитель'
    and not comment_lowercased contains 'всегда водитель виноват'
    and not comment_lowercased contains 'вы мне написали'
    and not comment_lowercased contains 'вы мне отправили'
    and not comment_lowercased contains 'вы мне пишете'
    and not comment_lowercased contains 'вы мне прислали'
    and not comment_lowercased contains 'вы мне присылаете'
    and not comment_lowercased contains 'вы мне шлете'
    and not comment_lowercased contains 'вы мне шлёте'
    and not comment_lowercased contains 'вы написали мне'
    and not comment_lowercased contains 'вы отправили мне'
    and not comment_lowercased contains 'вы пишете мне'
    and not comment_lowercased contains 'вы прислали мне'
    and not comment_lowercased contains 'вы присылаете мне'
    and not comment_lowercased contains 'вы шлете мне'
    and not comment_lowercased contains 'вы шлёте мне'
    and not comment_lowercased contains 'даже не разговарива'
    and not comment_lowercased contains 'доступ будет закрыт'
    and not comment_lowercased contains 'как будто я'
    and not comment_lowercased contains 'клиенты довольны'
    and not comment_lowercased contains 'когда такое было'
    and not comment_lowercased contains 'когда я так делал'
    and not comment_lowercased contains 'машина у меня'
    and not comment_lowercased contains 'мне прислали сообщение'
    and not comment_lowercased contains 'мне пришло сообщение'
    and not comment_lowercased contains 'не аккурат'
    and not comment_lowercased contains 'не было ни разу'
    and not comment_lowercased contains 'не было такого'
    and not comment_lowercased contains 'не в ту сторону'
    and not comment_lowercased contains 'не делал не разу'
    and not comment_lowercased contains 'не делал никогда'
    and not comment_lowercased contains 'не просил никого'
    and not comment_lowercased contains 'не разу не было'
    and not comment_lowercased contains 'не разу не просил'
    and not comment_lowercased contains 'ни разу ничего'
    and not comment_lowercased contains 'никогда не просил'
    and not comment_lowercased contains 'никогда не прошу'
    and not comment_lowercased contains 'нормально отношусь'
    and not comment_lowercased contains 'опасную езд'
    and not comment_lowercased contains 'остальные отзывы'
    and not comment_lowercased contains 'плавное'
    and not comment_lowercased contains 'постоянно пишите'
    and not comment_lowercased contains 'проветрива'
    and not comment_lowercased contains 'промокодчики'
    and not comment_lowercased contains 'такого не было'
    and not comment_lowercased contains 'такого небыло'
    and not comment_lowercased contains 'такого никогда не было'
    and not comment_lowercased contains 'хорошая машина'
    and not comment_lowercased contains 'я ни разу не'
    and not comment_lowercased contains 'я ни разу никого'
    and not comment_lowercased contains 'я никогда не грублю'
    and not comment_lowercased contains 'я никогда не отменяю'
    and not comment_lowercased contains 'я якобы'
    and not comment_lowercased contains 'якобы я'
    and not comment_lowercased contains 'пьян'
    and not comment_lowercased contains 'пиво'
    and not comment_lowercased contains 'пива'
    and not comment_lowercased contains 'алкогол'
    and not comment_lowercased contains 'наркот'
    and not comment_lowercased contains 'нарком'
    and not comment_lowercased contains 'не трезв'
    and not comment_lowercased contains 'нетрезв'
    and not comment_lowercased contains 'выпивш'
    and not comment_lowercased contains 'нецензур'
    and not comment_lowercased contains ' орет'
    and not comment_lowercased contains ' орёт'
    and not comment_lowercased contains ' хам'
    and not comment_lowercased contains 'поругал'
    and not comment_lowercased contains 'матом'
    and not comment_lowercased contains 'материт'
    and not comment_lowercased contains 'материл'
    and not comment_lowercased contains 'кричат'
    and not comment_lowercased contains 'груб'
    and not comment_lowercased contains 'конфликт'
    and not comment_lowercased contains 'спор'
    and not comment_lowercased contains 'нагл'
    and not comment_lowercased contains 'истери'
    and not comment_lowercased contains 'качать права'
    and not comment_lowercased contains 'неадекват'
    and not comment_lowercased contains 'скандал'
    and not comment_lowercased contains 'оскорб'
    and not comment_lowercased contains 'оскарб'
    and not comment_lowercased contains 'ругается'
    and not comment_lowercased contains 'ругаться'
    and not comment_lowercased contains ' агрес'
    and not comment_lowercased contains 'испачк'
    and not comment_lowercased contains 'засрал'
    and not comment_lowercased contains 'разлил'
    and not comment_lowercased contains 'пятна '
    and not comment_lowercased contains 'пятно '
    and not comment_lowercased contains 'чистк'
    and not comment_lowercased contains 'мусор'
    and not comment_lowercased contains 'гряз'
    and not comment_lowercased contains 'облил'
    and not comment_lowercased contains 'пролил'
    """,
    ],
)
async def test_smoke_recurtion(predicate_rule):
    pypred_predicate = pypred.Predicate(predicate_rule)
    lark_predicate = predicate.Predicate(predicate_rule)

    pypred_result = pypred_predicate.evaluate({})
    lark_result = lark_predicate.evaluate({})

    assert pypred_result == bool(lark_result)


async def test_smoke_topics(load_json):
    some_state = load_json('some_state.json')
    some_topics = load_json('some_topics.json')

    features = {
        key: feat['value']
        for key, feat in some_state['feature_layers'][-1].items()
    }

    topic_rules = [topic['rule_value'] for topic in some_topics['topics']]

    for topic_rule in topic_rules:
        pypred_predicate = pypred.Predicate(topic_rule)
        lark_predicate = predicate.Predicate(topic_rule)

        ppr = pypred_predicate.evaluate(features)
        lpr = lark_predicate.evaluate(features, as_bool=True)
        assert ppr == lpr
