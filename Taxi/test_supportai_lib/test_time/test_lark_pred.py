# flake8: noqa
# pylint: disable=expression-not-assigned
import timeit

import pytest

import openpyxl
import pypred

from supportai_lib import predicate
from supportai_lib import async_pipe


@pytest.fixture(name='scenarios_rules_static')
def _scenarios():
    return [
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
    ]


@pytest.fixture(name='scenarios_rules')
def _load(get_file_path, scenarios_rules_static):
    load_from_exel = False
    # load_from_exel = True

    def load_from_exel_():
        # Скачать экспорт правил из админки
        # переименовать
        g_1 = openpyxl.open(get_file_path('group_1.xlsx'))
        g_2 = openpyxl.open(get_file_path('group_2.xlsx'))
        g_3 = openpyxl.open(get_file_path('group_3.xlsx'))

        gs1 = g_1['scenarios']
        gs2 = g_2['scenarios']
        gs3 = g_3['scenarios']

        return [
            *(cell.value for cell in gs1['I']),
            *(cell.value for cell in gs2['I']),
            *(cell.value for cell in gs3['I']),
        ]

    return [
        *scenarios_rules_static,
        *(load_from_exel_() if load_from_exel else []),
    ]


def predicate_creation(klass, scenarios):
    res = []
    for scen in scenarios:
        scen: str
        scen = scen.replace('||', 'or')
        try:
            res.append(klass(scen, use_eval_cache=True))
        except Exception:  # pylint: disable=broad-except
            pass
    return res


def predicate_evaluate(preds):
    for pred in preds:
        pred.evaluate({})


@pytest.mark.xfail
async def test_time(scenarios_rules):
    print('TEST')
    timer = timeit.default_timer
    start = timer()
    preds = predicate_creation(predicate.Predicate, scenarios_rules)
    end = timer()
    lark_creation_time = end - start
    print(
        f'lark creation time {lark_creation_time} for {len(preds)}|{len(scenarios_rules)}',
    )

    start = timer()
    preds_ = predicate_creation(pypred.Predicate, scenarios_rules)
    end = timer()
    pred_creation_time = end - start
    print(
        f'pred creation time {pred_creation_time} for {len(preds_)}|{len(scenarios_rules)}',
    )

    start = timer()
    predicate_evaluate(preds)
    end = timer()
    lark_eval_time = end - start
    print(
        f'lark eval time {lark_eval_time} for {len(preds)}|{len(scenarios_rules)}',
    )

    start = timer()
    await predicate.execute_multiple(preds, {})
    end = timer()
    lark_eval_time = end - start
    print(
        f'lark eval time async {lark_eval_time} for {len(preds)}|{len(scenarios_rules)}',
    )

    start = timer()
    predicate_evaluate(preds_)
    end = timer()

    pred_eval_time = end - start
    print(
        f'pred eval time {pred_eval_time} for {len(preds_)}|{len(scenarios_rules)}',
    )


@pytest.mark.xfail
async def test_cpu_bound_time(scenarios_rules):
    print('TEST')
    timer = timeit.default_timer
    start = timer()
    preds = predicate_creation(predicate.Predicate, scenarios_rules)
    end = timer()
    lark_creation_time = end - start
    print(
        f'lark creation time {lark_creation_time} for {len(preds)}|{len(scenarios_rules)}',
    )

    start = timer()
    predicate_evaluate(preds)
    end = timer()
    lark_eval_time = end - start
    print(
        f'lark eval time {lark_eval_time} for {len(preds)}|{len(scenarios_rules)}',
    )

    start = timer()
    await predicate.execute_multiple(preds, {})
    end = timer()
    lark_eval_time = end - start
    print(
        f'lark eval time async {lark_eval_time} for {len(preds)}|{len(scenarios_rules)}',
    )

    timer = timeit.default_timer
    start = timer()
    applier = predicate.PredicateApplier(
        scenarios_rules, predicate.PredicateEngines.lark, as_bool=True,
    )
    end = timer()
    lark_creation_time = end - start
    print(
        f'lark creation time {lark_creation_time} for |{len(scenarios_rules)}',
    )

    pipe = async_pipe.Executor(applier, 1, workers=3)
    await pipe.start()

    start = timer()
    await pipe.assign([{}])
    end = timer()
    lark_eval_time = end - start
    print(f'lark eval time async {lark_eval_time} for {len(scenarios_rules)}')

    start = timer()
    [await predicate.execute_multiple(preds, {}) for _ in range(100)]
    end = timer()
    lark_eval_time = end - start
    print(
        f'lark eval time async m {lark_eval_time} for {len(preds)}|{len(scenarios_rules)}',
    )

    start = timer()
    [await pipe.assign([{} for _ in range(1)]) for x in range(100)]
    end = timer()
    lark_eval_time = end - start
    print(
        f'lark eval time async m {lark_eval_time} for {len(scenarios_rules)}',
    )

    await pipe.destroy()
