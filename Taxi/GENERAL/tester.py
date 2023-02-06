import allure
import datetime

from utils import utils, rules, exps
from classes.bsx_api_client import BsxClient
from classes.geotool_api_client import GeotoolClient
from classes.taxi_approvals_api_client import TaxiApprovalsClient
from classes.taxi_exp_api_client import TaxiExpClient


class IntegrationTester:
    def __init__(self):
        self.taxi_approvals = TaxiApprovalsClient()
        self.bsx = BsxClient()
        self.geotool = GeotoolClient()
        self.taxi_exp = TaxiExpClient()

    def close_all_rules_in_tariff_zones(self, tariff_zones, start, end):
        rules_to_close = self.bsx.get_single_ride_rules_in_tariff_zones(tariff_zones, start, end)
        rules_ids = []
        for rule in rules_to_close:
            # может оказаться так, что в правила попадают те, что были закрыты в результате предыдущих тест-кейсов
            # и их дата окончания может быть меньше, чем мы выставляем в close_at. биллинг это не примет
            # поэтому убираем такие правила из списка, они и так закроются к нужному времени
            expected_rule_end = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
            current_rule_end = datetime.datetime.fromisoformat(rule["end"])
            if current_rule_end > expected_rule_end:
                rules_ids.append(rule["id"])
        if rules_ids:
            service_name = "billing-subventions-x"
            api_path = "subventions_x_v2_close"
            close_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
            close_at = close_at.strftime('%Y-%m-%dT%H:%M:%S+03:00')
            data = {
                "rule_ids": rules_ids,
                "close_at": close_at
            }
            md_dict = self.taxi_approvals.create_multidraft_with_single_draft(service_name, api_path, data)
            md_id = md_dict["id"]
            self.taxi_approvals.wait_for_multidraft_status(md_id, "need_approval")
            self.taxi_approvals.approve_multidraft(md_id)
            self.taxi_approvals.wait_for_multidraft_status(md_id)

    def create_draft_to_update_experiment(self, exp_name):
        exp_data = self.taxi_exp.get_exp_with_name(exp_name)
        start = datetime.datetime.now()
        start_s = start.strftime('%Y-%m-%dT%H:%M:%S+03:00')
        exp_data['match']['action_time']['to'] = start_s

        params = {
            "name": exp_name,
            "last_modified_at": exp_data["last_modified_at"]
        }

        draft_dict = self.taxi_approvals.create_draft("taxi_exp", "taxi_exp_update_experiment", exp_data, params)
        return draft_dict

    def update_all_experiments_in_tariff_zones(self, tariff_zones):
        exps_names = set()
        for tariff_zone in tariff_zones:
            exps_list = self.taxi_exp.get_exps_in_tariff_zone(tariff_zone)
            for exp in exps_list:
                exps_names.add(exp["name"])
        draft_ids = []
        for exp_name in exps_names:
            draft_dict = self.create_draft_to_update_experiment(exp_name)
            draft_id = draft_dict["id"]
            draft_ids.append(draft_id)
            self.taxi_approvals.wait_for_draft_status(draft_id, "need_approval", timeout=5)
            self.taxi_approvals.approve_draft(draft_dict)
        for draft_id in draft_ids:
            self.taxi_approvals.wait_for_draft_status(draft_id)

    def approve_multidraft(self, md_id):
        self.taxi_approvals.approve_multidraft(md_id)
        self.taxi_approvals.wait_for_multidraft_status(md_id)

    def create_initial_rules(self, begin_at, end_at, tag=None, with_exps=False):
        if tag and with_exps:
            raise Exception("Can't create rules with exps and main tag at the same time.")
        if with_exps:
            payload = utils.get_payload('tests/json/v2_task_for_initial_rules_with_exp_close_candidates.json')
        else:
            payload = utils.get_payload('tests/json/v2_task_for_initial_rules_without_exp_close_candidates.json')
        payload["begin_at"] = begin_at
        payload["end_at"] = end_at
        if with_exps:
            payload["with_experiments"] = True
        else:
            payload["with_experiments"] = False
        if tag:
            payload["tag"] = tag
        with allure.step("Заводим правила через геотул."):
            # получаем из close_candidates state_hash, conflicting_rules, non_confflicting_rules
            state_hash, conflicting_rules, non_confflicting_rules = self.geotool.get_close_candidates(payload)
            # дополняем payload, который использовали для получения close_candidates полями, нужными для создания МД
            payload["activity_points"] = 0
            payload["state_hash"] = state_hash
            payload["close_rules_ids"] = []
            payload["close_experiments"] = []
            task_id = self.geotool.create_task_for_multidrafts(payload)
            self.geotool.wait_for_completed(task_id)
            md_rules_id, md_exp_id = self.geotool.get_multidraft_task_result(task_id)
        with allure.step("Аппрувим МД на правила."):
            self.approve_multidraft(md_rules_id)
        if with_exps:
            with allure.step("Аппрувим МД на эксперименты."):
                self.approve_multidraft(md_exp_id)
        else:
            assert md_exp_id is None, f"Experiments multidraft created, that was not expected. Multidraft ID is {md_exp_id}"
        return md_rules_id, md_exp_id

    def create_test_rules_and_exps(self, main_tag, with_exps, close_all_rules, exp_intersect, begin_at, end_at, tag):
        if main_tag and with_exps:
            raise Exception("Can't create rules with exps and main tag.")
        if exp_intersect:
            payload = utils.get_payload('tests/json/v2_task_with_exp_intersect_close_candidates.json')
        else:
            payload = utils.get_payload('tests/json/v2_task_without_exp_intersect_close_candidates.json')
        if main_tag:
            payload["tag"] = tag
        if with_exps:
            payload["with_experiments"] = True
        else:
            payload["with_experiments"] = False
        payload["begin_at"] = begin_at
        payload["end_at"] = end_at
        state_hash, conflicting_rules, non_confflicting_rules = self.geotool.get_close_candidates(payload)
        payload["state_hash"] = state_hash
        close_rules_ids = []
        close_experiments = []
        conflicting_to_close_rules, conflicting_optional_rules = rules.get_rules_ids_from_close_candidates(conflicting_rules)
        # non_conflicting_optional_rules, _ = rules.get_rules_ids_from_close_candidates(non_confflicting_rules)
        conflicting_to_close_exps, conflicting_optional_exp = exps.get_exps_from_close_candidates(conflicting_rules)
        # non_conflicting_optional_exps, _ = exps.get_exps_from_close_candidates(non_confflicting_rules)
        close_rules_ids.extend(conflicting_to_close_rules)
        close_experiments.extend(conflicting_to_close_exps)
        if close_all_rules:
            close_rules_ids.extend(conflicting_optional_rules)
            close_experiments.extend(conflicting_optional_exp)

        payload["close_experiments"] = close_experiments
        payload["close_rules_ids"] = close_rules_ids
        payload["activity_points"] = 0
        with allure.step("Заводим правила через геотул."):
            task_id = self.geotool.create_task_for_multidrafts(payload)
            self.geotool.wait_for_completed(task_id)
            md_rules_id, md_exp_id = self.geotool.get_multidraft_task_result(task_id)
        with allure.step("Аппрувим МД на правила."):
            self.approve_multidraft(md_rules_id)
        if not main_tag:
            if with_exps or exp_intersect:
                with allure.step("Аппрувим МД на эксперименты."):
                    self.approve_multidraft(md_exp_id)
            else:
                assert md_exp_id is None, f"Multidraft for experiments was created, that was not expected. Multidraft ID is {md_exp_id}"
        else:
            assert md_exp_id is None, f"Multidraft for experiments was created, that was not expected. Multidraft ID is {md_exp_id}"
        return md_rules_id, md_exp_id

    def assert_no_single_ride_rules_in_tariff_zones(self, tariff_zones, start, end):
        all_rules = self.bsx.get_single_ride_rules_in_tariff_zones(tariff_zones, start, end)
        active_rules = []
        for rule in all_rules:
            if not(rule["end"] == rule["start"]):
                active_rules.append(rule)
        assert active_rules == [], f"There are still active rules in tariff zones. {active_rules}"

    def assert_no_active_experiments_for_tariff_zones(self, tariff_zones):
        exps = []
        for tariff_zone in tariff_zones:
            exps_list = self.taxi_exp.get_exps_in_tariff_zone(tariff_zone)
            exps.extend(exps_list)
        assert exps == [], f"Some experiments were not updated and are still active: {exps}"

    def get_rules_by_multidraft_id(self, multidraft_id):
        drafts = self.taxi_approvals.get_drafts_attached_to_multidraft(multidraft_id)
        draft_ids = [draft["id"] for draft in drafts]
        added, closed = self.bsx.get_rules_by_draft_ids(draft_ids)
        return added, closed

    def get_rules_by_multidraft_ids(self, multidraft_ids):
        all_added = []
        all_closed = []
        for multidraft_id in multidraft_ids:
            new_added, new_closed = self.get_rules_by_multidraft_id(multidraft_id)
            all_added.extend(new_added)
            all_closed.extend(new_closed)
        return all_added, all_closed

    def get_exps_drafts_by_multidraft_id(self, multidraft_id):
        drafts_id_version = self.taxi_approvals.get_drafts_attached_to_multidraft(multidraft_id)
        drafts_exp_created = dict()
        drafts_exp_updated = dict()
        for d in drafts_id_version:
            draft = self.taxi_approvals.get_draft(d["id"])
            if draft["api_path"] == "taxi_exp_create_experiment":
                drafts_exp_created = draft
            elif draft["api_path"] == "taxi_exp_update_experiment":
                drafts_exp_updated = draft
        return drafts_exp_created, drafts_exp_updated

    def check_experiments(self, md_new_exp_id, md_init_exp_id, new_rules_start, new_rules_end,
                          main_tag, with_exps, close_all_rules, exp_intersect):
        # тут надо проверять только случаи, когда был создан драфт на эксперименты при создании правил
        # в зависимости от кейса создается или только драфт на "закрытие" эксперимента,
        # или драфт на "закрытие" и создание нового
        # или только драфт на создание нового
        # также для экспериментов надо проверять время действия
        if not main_tag and (with_exps or exp_intersect):
            initial_exp_draft, _ = self.get_exps_drafts_by_multidraft_id(md_init_exp_id)
            actual_exp_created, actual_exp_updated = self.get_exps_drafts_by_multidraft_id(md_new_exp_id)
            # if with_exps or exp_intersect:
            if with_exps and not exp_intersect:
                assert actual_exp_created, "No draft for new exp. "
                assert actual_exp_updated == {}, f"There is a draft for exp update {actual_exp_updated}, but it was not expected. "
                exps.check_created_exp(actual_exp_created, new_rules_end)
            elif not with_exps and exp_intersect:
                assert actual_exp_created == {}, f"There is a draft for new exp {actual_exp_created}, but it was not expected."
                assert actual_exp_updated, "No draft for exp update."
                exps.check_updated_exp(actual_exp_updated, initial_exp_draft, new_rules_start)
            elif with_exps and exp_intersect:
                assert actual_exp_created, "No draft for new exp."
                assert actual_exp_updated, "No draft for exp update."
                exps.check_created_exp(actual_exp_created, new_rules_end)
                exps.check_updated_exp(actual_exp_updated, initial_exp_draft, new_rules_start)

    def check_single_ride_rules(self,
                                md_init_rules_wo_tag, md_init_rules_w_tag, md_init_rules_w_exps, md_new_rules_id, tag,
                                start_date, end_date, main_tag, with_exps, close_all_rules, exp_intersect):

        # получаем изначально созданные правила (на этапе set up)
        initial_rules_wo_tag_added, _ = self.get_rules_by_multidraft_id(md_init_rules_wo_tag)
        initial_rules_w_tag_added, _ = self.get_rules_by_multidraft_id(md_init_rules_w_tag)
        initial_rules_w_exps_added, _ = self.get_rules_by_multidraft_id(md_init_rules_w_exps)

        # получаем правила, которые были добавлены в результате тест-кейса
        new_rules_added, actual_initial_closed_rules = self.get_rules_by_multidraft_id(md_new_rules_id)
        new_rules_tariff_zones = rules.get_rules_tariff_zones(new_rules_added)
        new_rules_tariff_classes = rules.get_rules_tariff_classes(new_rules_added)
        new_rules_geoareas = rules.get_rules_geoareas(new_rules_added)

        # тут выбираем, какие из исходных правил должны были быть закрыты
        expected_initial_closed_rules = rules.select_rules_to_be_closed(initial_rules_wo_tag_added,
                                                                        initial_rules_w_tag_added,
                                                                        initial_rules_w_exps_added,
                                                                        main_tag, with_exps, close_all_rules,
                                                                        exp_intersect)
        expected_closed_rules = rules.get_rules_ids(expected_initial_closed_rules)
        actual_closed_rules = rules.get_rules_ids(actual_initial_closed_rules)
        rules_diff = expected_closed_rules.symmetric_difference(actual_closed_rules)

        assert expected_closed_rules == actual_closed_rules, f"Expected closed rules differ from actual closed rules. "\
                                                             f"Difference: {rules_diff}.\n" \
                                                             f"Expected: {expected_closed_rules}.\n" \
                                                             f"Actual: {actual_closed_rules}"
        rules.check_added_rules(new_rules_added, new_rules_tariff_zones, new_rules_tariff_classes, new_rules_geoareas,
                                start_date, end_date, tag, main_tag, with_exps)
