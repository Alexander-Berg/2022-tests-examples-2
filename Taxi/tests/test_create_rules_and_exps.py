import allure
import pytest

from utils.utils import get_start_and_end_for_geotool

# Будем считать, что CLOSE_ALL_RULES - это закрытие только конфликтующих правил.
# Если CLOSE_ALL_RULES==true, то закрываем все conflicting_rules из close_candidates.
# Если CLOSE_ALL_RULES==false, то закрываем те, что should_close из conflicting_rules из close_candidates.
testcases = [
    # ({"main_tag": False, "with_exps": False, "close_all_rules": False, "exp_intersect": True}),  # 1
    # ({"main_tag": False, "with_exps": False, "close_all_rules": False, "exp_intersect": False}),  # 2
    # ({"main_tag": False, "with_exps": False, "close_all_rules": True, "exp_intersect": True}),  # 3
    # ({"main_tag": False, "with_exps": False, "close_all_rules": True, "exp_intersect": False}),  # 4
    # ({"main_tag": False, "with_exps": True, "close_all_rules": False, "exp_intersect": True}),  # 5
    # ({"main_tag": False, "with_exps": True, "close_all_rules": False, "exp_intersect": False}),  # 6
    ({"main_tag": False, "with_exps": True, "close_all_rules": True, "exp_intersect": True}),  # 7
    # ({"main_tag": False, "with_exps": True, "close_all_rules": True, "exp_intersect": False}),  # 8
    # ({"main_tag": True, "with_exps": False, "close_all_rules": False, "exp_intersect": True}),  # 9
    # ({"main_tag": True, "with_exps": False, "close_all_rules": False, "exp_intersect": False}),  # 10
    # ({"main_tag": True, "with_exps": False, "close_all_rules": True, "exp_intersect": True}),  # 11
    # ({"main_tag": True, "with_exps": False, "close_all_rules": True, "exp_intersect": False}),  # 12
]


def idfn(val):
    parts = []
    for k, v in val.items():
        parts.append(f"{k}: {v}")
    return ", ".join(parts)


@allure.suite('Проверка перезаведения правил через геотул.')
@allure.severity(allure.severity_level.CRITICAL)
@allure.link("https://testpalm.yandex-team.ru/testcase/exp_subv-46", "Test Palm")
@pytest.mark.parametrize("draft_params", testcases, ids=idfn)
def test_create_rules_and_exps(set_up, tag, draft_params):
    allure.dynamic.title(f"Test Case: {draft_params}")

    tester, md_init_rules_wo_tag, md_init_rules_w_tag, md_init_rules_w_exps, md_init_exp = set_up
    start_geotool, end_geotool = get_start_and_end_for_geotool()
    with allure.step("Заводим новые правила и эксперименты (в зависимости от кейса)"):
        md_new_rules_id, md_new_exp_id = \
            tester.create_test_rules_and_exps(begin_at=start_geotool, end_at=end_geotool, tag=tag, **draft_params)

        allure.dynamic.link(f"https://tariff-editor.taxi.tst.yandex-team.ru/drafts/multidraft/{md_new_rules_id}",
                            name="МД новых правил")
        if md_new_exp_id:
            allure.dynamic.link(f"https://tariff-editor.taxi.tst.yandex-team.ru/drafts/multidraft/{md_new_exp_id}",
                                name="МД новых экспериментов")
    with allure.step("Проверяем корректное закрытие и создание экспериментов."):
        tester.check_experiments(md_new_exp_id, md_init_exp, start_geotool, end_geotool, **draft_params)

    with allure.step("Проверяем корректное закрытие и создание правил single-ride."):
        tester.check_single_ride_rules(md_init_rules_wo_tag, md_init_rules_w_tag, md_init_rules_w_exps, md_new_rules_id,
                                   tag, start_geotool+"+03:00", end_geotool+"+03:00", **draft_params)
