import functools
import importlib
import os
import pathlib
import pkgutil
import re
import subprocess as sb
import sys
import tempfile
import typing as tp
import warnings
from collections import defaultdict, namedtuple

import cronlint
import pytest
import yaml
from textwrap import dedent

from dmp_suite.domain import DomainBase
from dmp_suite.domain.utils import collect_domains, get_default_domain_module
from dmp_suite.greenplum import GPTable
from taxidwh_settings import SettingsKeyNotFoundError, build_settings, Environment

from connection import yt
import sources_root
from dmp_suite import inspect_utils
from dmp_suite.inspect_utils import find_objects, get_imported_names
from dmp_suite.py_env.service_setup import Service
from dmp_suite.py_env.utils import get_root_config_path, get_service_config_path
from dmp_suite.ext_source_proxy.base import ExternalSourceProxy
from dmp_suite.ext_source_proxy.base import collect_external_source_proxies
from dmp_suite.replication.meta.dmp_integration import table
from dmp_suite.replication.meta.dmp_integration import rule_facade
from dmp_suite.replication.meta.entities import rules
from dmp_suite.replication.meta.entities.targets import yt_targets
from dmp_suite.replication.tasks.initialization import _InitializationTask
from dmp_suite.service_utils import get_service_by_module
from dmp_suite.table import ABSTRACT_TABLE_LIST, Table, LayeredLayout
from dmp_suite.task.base import AbstractTask, collect_tasks, is_task_module, ALLOWED_TASK_MODULE_SUFFIXES
from dmp_suite.task.cron import CRON_USER
from dmp_suite.task.reactive.trigger import Trigger
from dmp_suite.yt.task.logbroker import LogbrokerSource
from dmp_suite.yt import YTTable
from sources_root import SOURCES_ROOT

PYTHON_MODULE_INVOCATION = re.compile(r"python(3.7|2.7)?\s+-m\s+(?P<name>\S+)")
JAVA_INVOCATION = re.compile(r'java\s+')

YAML_EXTENSION = '.yaml'  # replication currently supports only .yaml

BASE_CLUSTERS = frozenset({
    yt.Cluster.HAHN,
    yt.Cluster.ARNOLD,
})

SPECIFIC_TABLE_CLUSTERS = {
    # replication doesn't support strict sequence replication
    # to multiple clusters
    'eda_bigfood_billing_export_payments_export': {yt.Cluster.HAHN},
    'eda_bigfood_billing_export_commissions_export': {yt.Cluster.HAHN},
}

DEPRECATED_DESTINATIONS = frozenset({
    'agglomerations_snp_raw',
    'auto_dictionary_raw',
    'callcenter_operators_operators_access_queue_etl_raw',
    'callcenter_operators_operators_access_queue_raw',
    'callcenter_stats_call_history_etl_raw',
    'callcenter_stats_call_history_raw',
    'callcenter_stats_operator_actions_etl_raw',
    'callcenter_stats_operator_actions_raw',
    'callcenter_stats_operator_history_etl_raw',
    'callcenter_stats_operator_history_raw',
    'cargo_claims_claims_raw_dmp',
    'cargo_claims_claims_raw_history_raw',
    'cars_catalog_prices_raw',
    'chatterbox_supporter_events_raw',
    'clowny_quotas_history_raw',
    'clowny_quotas_raw',
    'coop_accounts_accounts_raw_history',
    'coop_accounts_members_raw_history',
    'dbdrivers_raw',
    'dbdrivers_raw_history',
    'dbeda_eda_invoices_raw',
    'discount_rules',
    'eats_comp_mx_compensation_matrices_raw',
    'eats_comp_mx_compensation_packs_raw',
    'eats_comp_mx_compensation_packs_to_types_raw',
    'eats_comp_mx_compensation_types_raw',
    'eats_comp_mx_situation_groups_raw',
    'eats_comp_mx_situations_raw',
    'eda_analytics_courier_fines_new_snp_raw',
    'eda_bigfood_admins_snp_raw',
    'eda_bigfood_billing_export_commission_buff_hst_raw',
    'eda_bigfood_billing_export_commission_buff_raw',
    'eda_bigfood_billing_export_commissions_export',
    'eda_bigfood_billing_export_payment_buff_hst_raw',
    'eda_bigfood_billing_export_payment_buff_raw',
    'eda_bigfood_billing_export_payments_export',
    'eda_bigfood_brands_snp_raw',
    'eda_bigfood_carts_raw',
    'eda_bigfood_complaint_compensations_raw',
    'eda_bigfood_complaint_request_log_raw',
    'eda_bigfood_complaint_response_log_raw',
    'eda_bigfood_complaint_situation_types_raw',
    'eda_bigfood_complaint_situations_raw',
    'eda_bigfood_complaints_raw',
    'eda_bigfood_countries_snp_raw',
    'eda_bigfood_courier_advice_calculation_log_raw',
    'eda_bigfood_courier_advice_log_raw',
    'eda_bigfood_courier_auto_assignments_raw',
    'eda_bigfood_courier_delivery_zone_vert_snp_raw',
    'eda_bigfood_courier_delivery_zones_snp_raw',
    'eda_bigfood_courier_fns_cheques_raw',
    'eda_bigfood_courier_personal_data_raw',
    'eda_bigfood_courier_salary_adj_reasons_snp_raw',
    'eda_bigfood_courier_salary_adjustments_snp_raw',
    'eda_bigfood_courier_service_billing_d_snp_raw',
    'eda_bigfood_courier_services_snp_raw',
    'eda_bigfood_courier_shift_orders_raw',
    'eda_bigfood_courier_status_coordinates_raw',
    'eda_bigfood_couriers_assign_log_raw',
    'eda_bigfood_fns_api_requests_history_raw',
    'eda_bigfood_fns_api_requests_raw',
    'eda_bigfood_history_raw',
    'eda_bigfood_integration_order_statuses_raw',
    'eda_bigfood_logist_cour_tip_stts_hist_raw',
    'eda_bigfood_logistics_courier_tips_raw',
    'eda_bigfood_logistics_taxi_disp_requests_history_raw',
    'eda_bigfood_notifications_raw',
    'eda_bigfood_order_cancel_reactions_snp_raw',
    'eda_bigfood_order_cancel_reason_groups_snp_raw',
    'eda_bigfood_order_cancel_reasons_snp_raw',
    'eda_bigfood_order_cancel_tasks_raw',
    'eda_bigfood_order_courier_billings_history_raw',
    'eda_bigfood_order_courier_billings_raw',
    'eda_bigfood_order_feedbacks_p_c_l_snp_raw',
    'eda_bigfood_order_finance_info_raw',
    'eda_bigfood_order_fiscal_info_raw',
    'eda_bigfood_order_refunds_raw',
    'eda_bigfood_order_revision_compositions_raw',
    'eda_bigfood_order_revision_deliveries_raw',
    'eda_bigfood_order_revision_discounts_raw',
    'eda_bigfood_order_revision_item_options_raw',
    'eda_bigfood_order_revision_items_history_raw',
    'eda_bigfood_order_revision_items_raw',
    'eda_bigfood_order_revision_promocodes_raw',
    'eda_bigfood_order_surges_raw',
    'eda_bigfood_orders_history_raw',
    'eda_bigfood_orders_raw',
    'eda_bigfood_payment_flow_compositions_history_raw',
    'eda_bigfood_payment_flow_compositions_raw',
    'eda_bigfood_payment_flow_invoices_history_raw',
    'eda_bigfood_payment_flow_invoices_raw',
    'eda_bigfood_payment_flow_orders_history_raw',
    'eda_bigfood_payment_flow_orders_raw',
    'eda_bigfood_payment_flow_products_history_raw',
    'eda_bigfood_payment_flow_products_raw',
    'eda_bigfood_payment_flow_refunds_raw',
    'eda_bigfood_payments_raw',
    'eda_bigfood_payture_notifications_raw',
    'eda_bigfood_place_billing_act_contr_snp_raw',
    'eda_bigfood_place_billing_client_p_snp_raw',
    'eda_bigfood_place_billing_clients_snp_raw',
    'eda_bigfood_place_billing_contracts_history_raw',
    'eda_bigfood_place_billing_contracts_raw',
    'eda_bigfood_place_billing_person_p_snp_raw',
    'eda_bigfood_place_billing_persons_snp_raw',
    'eda_bigfood_place_categories_snp_raw',
    'eda_bigfood_place_client_c_p_m_c_snp_raw',
    'eda_bigfood_place_client_categories_raw',
    'eda_bigfood_place_commissions_snp_raw',
    'eda_bigfood_place_delivery_zone_vertices_hst_raw',
    'eda_bigfood_place_delivery_zone_vertices_raw',
    'eda_bigfood_place_delivery_zone_working_sc_raw',
    'eda_bigfood_place_delivery_zones_snp_raw',
    'eda_bigfood_place_info_snp_raw',
    'eda_bigfood_place_log_history_raw',
    'eda_bigfood_place_log_raw',
    'eda_bigfood_place_menu_categories_snp_raw',
    'eda_bigfood_place_menu_options_history_raw',
    'eda_bigfood_place_menu_options_raw',
    'eda_bigfood_place_phone_numbers_snp_raw',
    'eda_bigfood_place_schedule_raw',
    'eda_bigfood_place_tips_raw',
    'eda_bigfood_places_categories_snp_raw',
    'eda_bigfood_places_fines_by_orders_raw',
    'eda_bigfood_places_snp_raw',
    'eda_bigfood_popular_menu_items_snp_raw',
    'eda_bigfood_predefined_comments_snp_raw',
    'eda_bigfood_price_categories_snp_raw',
    'eda_bigfood_promo_bonuses_snp_raw',
    'eda_bigfood_promo_place_group_t_p_snp_raw',
    'eda_bigfood_promo_place_groups_snp_raw',
    'eda_bigfood_promo_requirements_snp_raw',
    'eda_bigfood_promo_schedule_snp_raw',
    'eda_bigfood_promo_types_snp_raw',
    'eda_bigfood_promocode_referrals_raw',
    'eda_bigfood_promocodes_phones_snp_raw',
    'eda_bigfood_promocodes_usage_raw',
    'eda_bigfood_promocodes_users_raw',
    'eda_bigfood_promos_snp_raw',
    'eda_bigfood_push_notifications_raw',
    'eda_bigfood_recurrent_payments_raw',
    'eda_bigfood_region_geobase_snp_raw',
    'eda_bigfood_region_settings_snp_raw',
    'eda_bigfood_regions_snp_raw',
    'eda_bigfood_schedule_redefined_dates_raw',
    'eda_bigfood_send_cheque_requests_raw',
    'eda_bigfood_vendor_order_status_hist_hst_raw',
    'eda_bigfood_vendor_order_status_hist_raw',
    'eda_bigfood_vendor_orders_hst_raw',
    'eda_bigfood_vendor_orders_raw',
    'eda_bigfood_vendor_restaurants_snp_raw',
    'eda_bigfood_vendor_roles_snp_raw',
    'eda_bigfood_vendor_user_restaurants_snp_raw',
    'eda_bigfood_vendor_users_history_raw',
    'eda_bigfood_vendor_users_raw',
    'eda_bigfood_vendor_users_roles_snp_raw',
    'eda_couriers_sch_analytics_timetable_raw',
    'eda_couriers_sch_courier_shift_states_raw',
    'eda_lavka_transport_courier_projct_tps_snp_raw',
    'eda_lavka_transport_courier_work_sttss_snp_raw',
    'eda_lavka_transport_couriers_history_raw',
    'eda_lavka_transport_couriers_raw',
    'eda_lavka_transport_places_snp_raw',
    'eda_lavka_transport_regions_snp_raw',
    'eda_lavka_transport_uniform_place_reloctns_raw',
    'eda_lavka_transport_uniform_sizes_snp_raw',
    'eda_lavka_transport_uniform_types_snp_raw',
    'eda_receipt_payture_receipt_info_history_raw',
    'eda_receipt_payture_receipt_info_raw',
    'eda_receipt_send_receipt_ofd_info_history_raw',
    'eda_receipt_send_receipt_ofd_info_raw',
    'eda_receipt_send_receipt_requests_history_raw',
    'eda_receipt_send_receipt_requests_raw',
    'eda_surge_surge_courier_zone_loads_log_raw',
    'eda_surge_surge_lavka_raw',
    'eda_surge_taxi_surger_raw',
    'feedbacks_raw',
    'log_admin_raw',
    'logistic_dispatcher_courier_advice_calc_log_history_raw',
    'logistic_dispatcher_courier_advice_calc_log_raw',
    'logistic_dispatcher_courier_prop_taxi_id_log_raw',
    'logistic_dispatcher_planned_transfers_history_hst_raw',
    'logistic_dispatcher_planned_transfers_history_raw',
    'logistic_dispatcher_rejections_history_hst_raw',
    'logistic_dispatcher_rejections_history_raw',
    'logistic_dispatcher_requests_history_hst_raw',
    'logistic_dispatcher_requests_history_raw',
    'oktell_hiring_stat_connections_1x1_wo_pd_raw',
    'order_proc_raw_hist',
    'order_proc_raw',
    'orders_raw',
    'unique_drivers_raw',
    'unique_drivers_raw_history',
    'wms_orders_dmp_raw',
    'wms_orders_dmp_raw_hist',
    'wms_product_groups_dmp_raw',
    'wms_products_dmp_raw',
    'wms_stores_dmp_raw',
})


class BaseChecks(object):
    def __init__(self):
        self._checks = set()

    def get(self):
        # Если запускать тесты в параллель, то pytest
        # не нравится, когда данные параметризованных тестов
        # отличаются для разных процессов. Поэтому тут нужно
        # упорядочить функции по имени.
        result = list(self._checks)
        result.sort(key=lambda func: func.__name__)
        return result

    def __call__(self, fn):
        self._checks.add(fn)
        return fn


base_workflow_checks = BaseChecks()


def get_workflow_path(etl_service):
    #type: (Service) -> str
    return os.path.join(
        etl_service.home_dir,
        'workflow'
    )


def assert_cronfile(filepath, user):
    args = namedtuple('Args', ['crontab', 'check_username', 'whitelisted_users'])
    args.crontab = filepath
    args.check_username = True
    args.whitelisted_users = ['www-data']

    assert os.path.isfile(args.crontab)

    counter = cronlint.LogCounter()
    exit_code = cronlint.check_crontab(args, counter)
    assert exit_code == 0, \
        'Cron file "{}" has errors or warnings'.format(args.crontab)


@base_workflow_checks
def check_cronfile(etl_service):
    assert_cronfile(
        os.path.join(
            get_workflow_path(etl_service),
            'crontabs',
            'workflow-cron-production'),
        'www-data'
    )


@base_workflow_checks
def check_task_cronfile(etl_service):
    with tempfile.NamedTemporaryFile() as lxc_task_cron, \
            tempfile.NamedTemporaryFile() as rtc_task_cron, \
            tempfile.NamedTemporaryFile() as rtc_sh_cron:
        task_cron_py = os.path.join(
            SOURCES_ROOT, 'tools', 'generator', 'task_cron.py')

        cmd = [
            sys.executable, task_cron_py, etl_service.name,
            '--lxc-task-cron-path', lxc_task_cron.name,
            '--rtc-task-cron-path', rtc_task_cron.name,
            '--rtc-sh-cron-path', rtc_sh_cron.name,
        ]
        kwargs = dict(
            stdout=sb.DEVNULL,
            stderr=sb.PIPE
        )
        # запускаем в subprocess, чтобы проверить генерацию крона
        # в условиях аналогичных релизу - в тестах питонячие модули
        # загружены уже с пропатченными конфигами
        with sb.Popen(cmd, **kwargs) as process:
            stdout, stderr = process.communicate()
            returncode = process.poll()
            if returncode:
                stderr = stderr.decode('utf-8')
                raise RuntimeError(f'cron generation error\n{stderr}')

        assert_cronfile(lxc_task_cron.name, CRON_USER)
        assert_cronfile(rtc_task_cron.name, CRON_USER)
        assert_cronfile(rtc_sh_cron.name, CRON_USER)


@base_workflow_checks
def check_all_tasks_were_scheduled(etl_service):
    # Нам надо, чтобы все таски были поставлены на крон, или
    # было явно помечено, что их будут запускать вручную.
    #
    # Таск может либо сам иметь расписание запусков, либо
    # являться частью цепочки, которая запускается по расписанию.
    #
    # Кроме того, если таск отмечен, как manual, но при этом так же
    # запускается по крону, то это не нормальная ситуация и её мы будем
    # тоже считать ошибкой.

    # Сначала найдём все таски
    task_bounds = collect_tasks(etl_service.name)
    all_tasks = [tb.task for tb in task_bounds]

    # Затем построим "дерево" из которого можно будет найти родителей таска
    # От одного таска могут зависеть несколько других, поэтому составляем список "родителей".
    child_to_parents = defaultdict(list)

    for parent_task in all_tasks:
        for child_task in parent_task.get_required_tasks():
            child_to_parents[child_task].append(parent_task)

    # Затем уберём из них те, для которых известно расписание
    def has_cron(task: AbstractTask):
        if task.scheduler is not None:
            return True
        parents = child_to_parents[task]
        return any(map(has_cron, parents))

    tasks = [t for t in all_tasks if not has_cron(t)]

    # А так же, уберём таски с ручным запуском
    def is_manual(task: AbstractTask):
        if task._manual:
            return True
        parents = child_to_parents[task]
        return any(map(is_manual, parents))

    tasks = [t for t in tasks if not is_manual(t)]

    # Если в результате что-то осталось, то это неправильно
    assert len(tasks) == 0, 'У этих тасков нет расписания:\n  - {}'.format(
        '\n  - '.join(t.name for t in tasks)
    )

    # Теперь проверим, что нет тасков, помеченных manual, но стоящих на кроне
    manual_tasks = [t for t in all_tasks if t._manual]
    manual_tasks_with_cron = [t for t in manual_tasks if has_cron(t)]

    assert len(manual_tasks_with_cron) == 0, 'Эти таски помечены как "manual", но будут запускаться по крону:\n  - {}'.format(
        '\n  - '.join(t.name for t in manual_tasks_with_cron)
    )


@base_workflow_checks
def check_no_schedulers_removed_from_lxc_and_not_added_to_rtc(etl_service):
    # В сервисе не должно быть тасков у которых enable_rtc=False и disable=True,
    # иначе это приведёт к тому, что такой таск не будет нигде запускаться

    # Сначала найдём все таски
    task_bounds = collect_tasks(etl_service.name)
    all_tasks = [tb.task for tb in task_bounds]
    tasks_with_scheduler = [t for t in all_tasks if t.scheduler is not None]
    tasks_with_wrong_flags = [
        t
        for t in tasks_with_scheduler
        if t.scheduler.disable_lxc and not t.scheduler.enable_rtc
    ]
    if tasks_with_wrong_flags:
        names = [t.name for t in tasks_with_wrong_flags]
        names.sort()
        names_as_str = '\n'.join(f'- {name}' for name in names)
        raise AssertionError(f'These tasks have been disabled at LXC but not enabled at RTC:\n{names_as_str}')



@base_workflow_checks
def check_all_tasks_have_unique_names(etl_service):
    # Сначала найдём все таски
    task_bounds = collect_tasks(etl_service.name)
    tasks = [tb.task for tb in task_bounds]

    name_to_tasks = defaultdict(list)

    for task in tasks:
        name_to_tasks[task.name].append(task)

    # А так же, уберём таски с ручным запуском
    duplicates = [
        (name, tasks)
        for name, tasks in name_to_tasks.items()
        if len(tasks) > 1
    ]

    # Если в результате что-то осталось, то это неправильно
    assert len(duplicates) == 0, 'У этих тасков одинаковые имена:\n  - {}'.format(
        '\n  - '.join(
            '{} -> {}'.format(
                name,
                ', '.join(map(str, tasks))
            )
            for name, tasks in duplicates
        )
    )


def _is_task_from_service(task: AbstractTask, check_in_service: str) -> bool:
    """ Проверить, совпадает ли сервис, где таск определен, с сервисом `check_in_service` """
    primary_module = task.get_primary_module()
    task_service_name = get_service_by_module(primary_module)
    return task_service_name == check_in_service


@base_workflow_checks
def check_cross_service_task_imports(etl_service):
    """
    Проверка на то, чтобы в сервисе не импортировались таски из стороннего сервиса.
    Важно исключать кросс-сервисное использование тасков, потому что они могут использовать
    чужую конфигурацию и доступы, отчего таск и, соответственно, граф может постоянно падать.

    Для проверки посмотрим модуль, в котором таск был определён.
    Сравним с именем сервиса, для которого был запущен тест.
    Так сделаем для всех тасков, найденных в сервисе.
    """
    cross_imports = {}
    service_name = etl_service.name
    task_bounds = collect_tasks(etl_service.name)
    for task_bound in task_bounds:
        task = task_bound.task

        if task in cross_imports:
            continue  # Дважды можно не проверять

        # Если сервис таска отличается от сервиса, для которого запущен тест, то он импортирован извне
        if not _is_task_from_service(task, service_name):
            paths = [f"    - {bound_path.module.__name__}"
                     for bound_path in task_bound.bound_paths
                     if bound_path.module.__name__ != task.get_primary_module() and
                     get_service_by_module(bound_path.module.__name__) == service_name]
            cross_imports[task] = "\n".join(paths)

        # Также проверим для зависимостей таска
        for required_task in task.get_required_tasks():
            if (required_task not in cross_imports) and not _is_task_from_service(required_task, service_name):
                # Место импорта укажем модуль таска, который зависит от него
                cross_imports[required_task] = f"    - {task.get_primary_module()}"

    msg = "\n".join(f" - {task.name}.\n   Возможные места импортов:\n{paths}" for task, paths in cross_imports.items())
    assert len(cross_imports) == 0, f"Следующие таски импортируются из сторонних сервисов:\n{msg}"


@base_workflow_checks
def check_correct_task_primary_module(etl_service):
    """
    Проверка корректного выявления primary_module (модуля, в котором определен таск).

    Соберём все таски сервиса, найдём путь, в котором таск был определен, а не импортирован, сравним с primary_module.
    """
    service_name = etl_service.name
    task_bounds = collect_tasks(service_name)
    imported: tp.Dict['ModuleType', tp.Set[str]] = {}
    wrong_primary_modules = []
    for task_bound in task_bounds:
        task = task_bound.task
        for bound in task_bound.bound_paths:
            module = bound.module
            if module not in imported:
                # Найдём все импорты в файле, чтобы отличить импорт таска от места его определения
                imported[module] = inspect_utils.get_imported_names(module)

            if bound.name not in imported[module]:
                if task.get_primary_module() != module.__name__:
                    wrong_primary_modules.append(f"   Таск: '{task.name}'. Ожидался: {module.__name__}. Получен: {task.get_primary_module()}")

    assert len(wrong_primary_modules) == 0, "У этих тасков неверный primary_module:\n" + "\n".join(wrong_primary_modules)


def _non_task_module_filter(module_name: str, is_package: bool) -> bool:
    """ Инверсия для `loader_filter` """
    components = module_name.split('.')
    is_migration = len(components) >= 2 and components[1] == 'migrations'
    if is_migration:
        # Пропустить миграции
        return False
    return is_package or not is_task_module(module_name)


@base_workflow_checks
def check_for_non_task_module_tasks(etl_service: Service):
    """
    Проверить, не был ли определен таск в файле, который не будет собираться функцией `collect_tasks`.
    """

    tasks: tp.List[tp.Tuple[AbstractTask, 'ModuleType']] = []
    imported_names: tp.Dict['ModuleType', tp.Set[str]] = {}

    def task_filter(obj):
        try:
            return isinstance(obj, AbstractTask)
        except AttributeError:
            # `Record` has no __class__ attribute
            return False

    for task_module, attr_name, task in find_objects(
            etl_service.name,
            filters=[task_filter],
            modules_filters=[_non_task_module_filter],
            return_object_only=False,
            skip_import_errors=False,
    ):
        if isinstance(task, _InitializationTask):
            continue

        imported_names_in_module = imported_names.get(task_module, None)
        if imported_names_in_module is None:
            imported_names_in_module = imported_names[task_module] = get_imported_names(task_module)

        if attr_name not in imported_names_in_module:
            tasks.append((task, task_module))

    allowed_modules = ", ".join(f"`{task_module_suffix}.py`" for task_module_suffix in ALLOWED_TASK_MODULE_SUFFIXES)
    msg = "\n  ".join(f"Found task '{task.name}' in module: `{module.__name__}`" for task, module in tasks)
    assert len(tasks) == 0, f"Allowed module names for tasks are: {allowed_modules}.\n" \
                            f"Some tasks were declared in wrong files:\n  {msg}"


@base_workflow_checks
def check_cross_service_domain_imports(etl_service: Service):
    """
    Проверка на кросс-сервисное использование доменов.

    Соберем для сервиса все домены и все таблицы.
    Если у какой-либо таблицы домен не совпадет с найденными, значит этот домен из стороннего сервиса.
    """
    domains_package = get_default_domain_module(etl_service.name)
    tables_package = etl_service.name + '.layer'

    domains = collect_domains(domains_package)
    imported: tp.Dict[tp.Type[Table], str] = {}

    tables = inspect_utils.find_tables(tables_package, (Table,))

    # FIXME: Эти таблицы на данный момент импортируют домены
    #        После DMPDEV-4819 надо удалить эти исключения
    excluded_tables = []
    if etl_service.name == "taxi_etl":
        from taxi_etl.layer.yt.cdm.geo.dim_geo_node.table import YTDimGeoNode
        excluded_tables.append(YTDimGeoNode)
        from taxi_etl.layer.yt.cdm.geo.link_geo_node_tariff_zone.table import YTLinkGeoNodeTariffZone
        excluded_tables.append(YTLinkGeoNodeTariffZone)

    for table in tables:
        table: tp.Type[Table]
        if get_service_by_module(table.__module__) != etl_service.name:
            # Таблица импортировалась из другого сервиса
            continue

        if table in excluded_tables:
            # FIXME: DMPDEV-4819
            # На момент написания теста, некоторые таблицы импортировали домены.
            # Чтобы можно было добавить этот тест, добавил временные исключения.
            # Как только всё будет перенесено, надо эту проверку удалить.
            continue

        try:
            layout = table.get_layout()
        except AttributeError:
            continue    # Скорее всего, абстрактная таблица без layout

        if isinstance(layout, LayeredLayout):   # Домены указываются только в LayeredLayout
            domain = layout.domain
            if domain is not None:
                if domain not in domains:
                    imported[table] = f" - Модуль: `{table.__module__}`. Таблица `{table.__name__}` импортирует домен `{domain}`"

    msg = "\n".join(imported.values())
    assert len(imported) == 0, f"Сервис `{etl_service.name}` импортирует домены из других сервисов:\n{msg}"


def _domain_full_name(domain: 'DomainBase') -> str:
    """ Имя домена с его типом для отображения в сообщении теста """
    return f"{domain.prefix_key}.{domain.type.code}.{domain.code}"


@base_workflow_checks
def check_unique_domain_names(etl_service: Service):
    """
    Проверка уникальности имен доменов `prefix_key.name` внутри одного сервиса
    """
    domains_package = get_default_domain_module(etl_service.name)
    domains = collect_domains(domains_package)

    domain_names = defaultdict(list)
    for domain in domains:
        domain_names[domain.unique_name].append(domain)

    # TODO: Временные исключения. Будут исправлены в DMPDEV-5243
    excluded_domain_names = [
        "taxi.callcenter",
        "taxi.logistic",
        "taxi.shortcut",
        "taxi.executor_acquisition",
    ]

    for exclude_name in excluded_domain_names:
        domain_names.pop(exclude_name, None)

    collided = []
    for unique_name, domain_list in domain_names.items():
        if len(domain_list) > 1:
            domains_str = ", ".join(map(_domain_full_name, domain_list))
            collided.append(f' - Имя "{unique_name}". Домены: {domains_str}')

    msg = f"В сервисе {etl_service.name} найдены домены с одинаковыми именами:\n" + "\n".join(collided)
    assert len(collided) == 0, msg


@base_workflow_checks
def check_logbroker_doc_config(etl_service):
    task_bounds = collect_tasks(etl_service.name)
    tasks = [tb.task for tb in task_bounds]

    topic_not_set = []

    root_config_path = get_root_config_path()
    service_config_path = get_service_config_path(etl_service.name)

    settings = build_settings(
        os.path.join(root_config_path, 'default'),
        os.path.join(service_config_path, 'default'),
    )

    for task in tasks:
        for source in task.get_sources():
            if isinstance(source, LogbrokerSource):
                try:
                    settings(f'logbroker.connections.{source.name}.topic')
                except SettingsKeyNotFoundError:
                    topic_not_set.append(task)

    assert len(topic_not_set) == 0, 'У этих тасков не добавлен топик в default/logbroker.yaml: \n {}'.format(
        '\n - '.join('{} -> {}'.format(task.name, task) for task in topic_not_set)
    )


@base_workflow_checks
def check_all_scripts_executable(etl_service, optional=True):
    for script in _collect_scripts(etl_service, optional):
        assert os.access(script, os.X_OK), \
            'File is not executable {}'.format(script)


def _collect_scripts(etl_service, optional):
    scripts_path = os.path.join(
        get_workflow_path(etl_service),
        'scripts'
    )
    assert os.path.isdir(scripts_path) or optional

    for current_dir, _, files in os.walk(scripts_path):
        for script in files:
            if script.endswith('.sh'):
                yield os.path.join(current_dir, script)


def _collect_files(etl_service):
    files = set()
    scripts_path = os.path.join(
        get_workflow_path(etl_service),
        'scripts'
    )
    for root_dir, _, filenames in os.walk(scripts_path):
        rel_root_dir = os.path.relpath(root_dir, scripts_path)
        files.update(
            os.path.join(rel_root_dir, f) for f in filenames
        )
    return files


@base_workflow_checks
def check_modules_in_scripts(etl_service, optional=True):

    for script in _collect_scripts(etl_service, optional):
        modules = None
        last_error_message = None
        try:
            full_script_name = os.path.basename(script)
            modules = _check_modules_in_script(script)
        except ModuleCheckError as e:
            if e.critical:
                raise
            last_error_message = str(e)
            warnings.warn(UserWarning(last_error_message))

        has_java = check_java_invocation(script)
        if not modules and not has_java:
            raise AssertionError("No python modules invoked in {} ({})".format(
                os.path.basename(script),
                last_error_message,
            ))


@base_workflow_checks
def check_no_new_sh_scripts_is_added(etl_service, optional=True):
    try:
        added_files = sb.check_output(['git', 'diff', '--name-only', '--diff-filter=A', 'origin/develop'])
    except sb.CalledProcessError:
        return
    scripts = set(_collect_scripts(etl_service, optional))
    for file in map(lambda f: f.decode('utf-8'), filter(None, added_files.split(b'\n'))):
        if os.path.abspath(file) in scripts:
            raise AssertionError(
                "Adding new scripts is forbidden. Use tasks instead. Script found: {} ".format(file))


@base_workflow_checks
def check_all_external_reactor_sources_findable(etl_service):
    task_bounds = collect_tasks(etl_service.name)

    source_proxies_by_collect_tasks = set()
    source_proxies = set(collect_external_source_proxies(etl_service.name))

    for bound in task_bounds:
        if isinstance(bound.task.scheduler, Trigger):
            for entity, _ in bound.task.scheduler.parameters():
                if isinstance(entity, ExternalSourceProxy):
                    source_proxies_by_collect_tasks.add(entity)

    assert source_proxies == source_proxies_by_collect_tasks


@base_workflow_checks
def check_all_external_source_proxies_have_propper_ctl_entity(etl_service):
    source_proxies = set(collect_external_source_proxies(etl_service.name))
    for s in source_proxies:
        assert isinstance(s.ctl_entity, str)


def check_java_invocation(script):
    with open(script) as f:
        for line in f:
            match = JAVA_INVOCATION.search(line)
            if match is not None:
                return True
    return False


def _check_modules_in_script(script):
    modules = []
    with open(script) as f:
        for line in f:
            try:
                modules.extend(_check_modules_in_line(line))
            except ModuleCheckError as e:
                e.script = script
                raise
    return modules


def _check_modules_in_line(line):
    match = PYTHON_MODULE_INVOCATION.search(line)
    if match is None:
        return []
    module = match.group('name')

    try:
        loader = pkgutil.find_loader(module)
    except Exception as e:
        raise CouldNotImportModule(module, e)
    if loader is None:
        raise NoSuchModule(module)

    try:
        importlib.import_module(module)
    except Exception as e:
        raise CouldNotImportModule(module, e, critical=False)

    return [module]


class ModuleCheckError(Exception):
    def __init__(self, module, script=None, critical=True):
        super(ModuleCheckError, self).__init__()
        self.module = module
        self.script = script
        self.critical = critical


class NoSuchModule(ModuleCheckError):
    def __str__(self):
        return "No such module: {} (mentioned in {})".format(
            self.module, os.path.basename(self.script)
        )


class CouldNotImportModule(ModuleCheckError):
    def __init__(self, module, exception, script=None, critical=True):
        super(CouldNotImportModule, self).__init__(
            module, script=script, critical=critical
        )
        self.exception = exception

    def __str__(self):
        return "Could not import module {} (mentioned in {}): {}".format(
            self.module, os.path.basename(self.script), self.exception
        )


@pytest.mark.parametrize(
    ('line', 'expected'),
    [
        ('#!/bin/bash\n', []),
        ('\n', []),
        ('python3.7 -m dmp_suite.runner\n', ['dmp_suite.runner']),
    ]
)
def test_modules_in_line(line, expected):
    assert _check_modules_in_line(line) == expected


@base_workflow_checks
def check_service_has_gp_ttl_task(etl_service):
    from dmp_suite.greenplum.maintenance.partition.expired import ExpiredPartitionMaintenanceTask
    # Сначала найдём все таски
    task_bounds = collect_tasks(etl_service.name)
    service_name = etl_service.name
    if os.getenv('DMP_SERVICE_NAME') is None:
        # Хак на случай, если тесты выполняются без ETL-сервиса
        # На этот момент все сервисы и таски уже были вычислены
        # поэтому патчить будет сложнее, чем сделать так
        service_name = 'root_etl'
    ttl_task_names = {
        service_name + '_' + t
        for t in ('cleanup_gp_partition_by_ttl', 'relocation_nvme_to_ssd')
    }
    for tb in task_bounds:
        if isinstance(tb.task, ExpiredPartitionMaintenanceTask) and tb.task.name in ttl_task_names:
            ttl_task_names.remove(tb.task.name)
            if not ttl_task_names:
                return
    assert False


def _has_py_files(path):
    # Возвращает True если в директории или одной из
    # поддиректорий есть хотя бы один .py файл
    for dirname, subdirs, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                return True
    return False


@base_workflow_checks
def check_init_files(etl_service, optional=False):
    # Внутри директории сервиса всё должно быть python модулем.
    # Новые пользователи DMP, создавая таски, часто про это забывают
    # и в итоге эти таски не добавляяются в расписание.
    #
    # При этом разрешается иметь директории без __init__.py,
    # если внутри неё нет ни одного .py файла. Такое у нас иногда
    # бывает например если в директории сложены только SQL.

    root_dir = os.path.join(
        etl_service.home_dir,
        etl_service.name
    )

    for dirname, subdirs, files in os.walk(root_dir):
        if '__pycache__' in subdirs:
            # в поддиректории кэша нам спускаться не надо
            subdirs.remove('__pycache__')

        if '__init__.py' not in files and _has_py_files(dirname):
            raise AssertionError(f'Please, add __init__.py to {dirname} to make it a proper Python module.')


@functools.lru_cache()
def _collect_tables(module) -> tp.Set[tp.Type[table.ReplicationTable]]:
    def table_loader_filter(module_name: tp.Text, is_package: bool):
        return is_package or 'table' in module_name

    def table_filter(obj):
        return (
            isinstance(obj, type)
            and issubclass(obj, table.ReplicationTable)
            and obj is not table.ReplicationTable
        )

    return inspect_utils.find_objects(
        module, filters=[table_filter], modules_filters=[table_loader_filter],
    )


def _collect_rules(etl_service) -> tp.Iterable[rule_facade.RuleFacade]:
    for tbl in _collect_tables(etl_service.name):
        yield tbl.__replication_target__.rule_facade


@base_workflow_checks
def check_non_partitioned_tables_are_placed_in_folder_with_same_name(etl_service):
    errors = []

    for rf in _collect_rules(etl_service):
        destination = tp.cast(rules.YtDestination, rf.destination)

        target = tp.cast(yt_targets.YTTarget, rf.target)

        if target.partitioning is not None:
            continue

        head, folder, table = destination.target.path.rsplit('/', 2)

        if table == folder:
            continue

        errors.append(destination.target.path)

    tables_list = '\n'.join(errors)
    assert not errors, (
        'Non partitioned tables must be placed in folders with same name. '
        f'Check tables: {tables_list}'
    )


@base_workflow_checks
def check_tables_replicated_to_2_clusters(etl_service):
    errors = []

    for rf in _collect_rules(etl_service):
        destination = tp.cast(rules.YtDestination, rf.destination)

        destination = tp.cast(rules.YtDestination, destination)
        clusters = set(destination.target.yt_clusters)

        if destination.name in SPECIFIC_TABLE_CLUSTERS:
            expected_clusters = SPECIFIC_TABLE_CLUSTERS[destination.name]
            assert clusters == expected_clusters, (
                f'{destination.name} mentioned as replicated '
                f'to {expected_clusters}, but replicated to {clusters}'
            )
            continue

        if clusters != BASE_CLUSTERS:
            errors.append(destination.name)

    assert not errors, (
        f'This tables should be replicated to '
        f'{{{", ".join(c .name for c in BASE_CLUSTERS)}}} or mentioned '
        f'in SPECIFIC_TABLE_CLUSTERS'
    )


@base_workflow_checks
def check_all_new_targets_created_with_raw_mapper(etl_service):
    errors = []

    for rf in _collect_rules(etl_service):
        destination = tp.cast(rules.YtDestination, rf.destination)

        destination = tp.cast(rules.YtDestination, destination)

        if destination.name in DEPRECATED_DESTINATIONS:
            assert destination.mapper != '$raw', (
                f'Please, remove {destination.name} from '
                f'DEPRECATED_DESTINATIONS since it has $raw mapper'
            )
            continue

        if destination.mapper != '$raw':
            errors.append(destination.name)

    assert not errors, 'All new destinations must be created with $raw mapper'


@base_workflow_checks
def check_path_to_destination_matches_path_to_source(etl_service):
    rules_dir = os.path.join(sources_root.SOURCES_ROOT, sources_root.RULES)

    errors = []

    for rf in _collect_rules(etl_service):

        dwh_rule_path = pathlib.Path(rf.rule_filename)
        dwh_rule_rel_path = dwh_rule_path.relative_to(rules_dir)

        expected_base_rule_path = pathlib.Path(rules_dir).joinpath(
            sources_root.RULES, *dwh_rule_rel_path.parts[1:],
        )

        expected_base_rule_rel_path = expected_base_rule_path.relative_to(
            rules_dir
        )

        try:
            with open(expected_base_rule_path, 'rt') as f:
                raw_rule = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            errors.append(
                f'Source rule for {rf.rule.name} (placed in '
                f'{dwh_rule_rel_path}) is expected to be at '
                f'{expected_base_rule_rel_path}, but it wasn\'t found there'
            )
            continue

        raw_rule_name = raw_rule.get('name')

        if raw_rule_name != rf.rule.name:
            errors.append(
                f'Source rule for {rf.rule.name} (placed in '
                f'{dwh_rule_rel_path}) is expected to be at '
                f'{expected_base_rule_rel_path}, but {raw_rule_name} was '
                f'found there'
            )

    for error in errors:
        # make test errors more readable
        print(error)

    assert not errors


@base_workflow_checks
def check_imports(etl_service):
    # Внутри директории сервиса всё python файлы должны быть
    # импортируемы без ошибок.

    root_dir = os.path.join(
        etl_service.home_dir,
        etl_service.name
    )

    for dirname, subdirs, files in os.walk(root_dir):
        relative_dirname = dirname[len(root_dir):].strip('/')

        if '__pycache__' in subdirs:
            # в поддиректории кэша нам спускаться не надо
            subdirs.remove('__pycache__')

        for file in files:

            if file.endswith('.py'):
                module_name = etl_service.name
                if relative_dirname:
                    module_name += '.' + relative_dirname.replace('/', '.')
                if file != '__init__.py':
                    module_name += '.' + file.rsplit('.', 1)[0]

                importlib.import_module(module_name)


@base_workflow_checks
def check_unique_yt_layouts(etl_service):
    if etl_service.name == 'dmp_suite':
        return

    tables = set(
        inspect_utils.find_tables(
            module=etl_service.name,
            table_base_classes=(YTTable, ),
            table_blacklist=ABSTRACT_TABLE_LIST
        )
    )

    layout_to_tables = defaultdict(list)

    for table in tables:
        # Скипаем классы с некорректными и пустыми лэйаутами
        # Это могут быть базовые классы, тогда мы проверим их наследников
        try:
            table_layout = table.get_layout()  # type: ignore
            if table_layout is None:
                continue
        except:
            continue

        if table_layout is not None:
            layout_to_tables[table_layout].append(table)

    errors = []
    for lst in layout_to_tables.values():
        if len(lst) > 1:
            errors.append(tuple(lst))

    if errors:
        raise AssertionError(
            'These tables do not have a unique layout:\n' +
            ';\n'.join(map(str, errors))
        )


@base_workflow_checks
def check_unique_greenplum_layouts(etl_service):
    if etl_service.name == 'dmp_suite':
        return

    gp_blacklist = set()
    if etl_service.name == 'eda_etl':
        from eda_etl.layer.greenplum.dds_hnhm.marketplace.order import Order
        gp_blacklist = {Order}

    if etl_service.name == 'taxi_etl':
        from taxi_etl.layer.greenplum.rep.finance.dm_amr_geo_node_additive.common.view import DmAmrGeoNodeAdditiveBase
        from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_sh_metric.common.view import AggTariffZoneSHMetricBase
        from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_subsidy_metric.common.view import \
            AggTariffZoneSubsidyMetricBase
        from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_candidate_metric.common.view import \
            AggTariffZoneTariffClassCandidateMetricBase
        from taxi_etl.layer.greenplum.rep.finance.dm_amr_geo_node_sh.common.view import DmAmrGeoNodeSHBase
        from taxi_etl.layer.greenplum.rep.finance.dm_amr_geo_node.common.view import DmAmrGeoNodeBase
        from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_metric.common.view import AggTariffZoneMetricBase
        from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_dlos_metric.common.view import \
            AggTariffZoneTariffClassDlosMetricBase
        from taxi_etl.layer.greenplum.stg.dbtaxi.agglomerations.agglomeration_op_manager_link.table import \
            WrkDbtaxiDimGeoNodeOperationalManager
        from taxi_etl.layer.greenplum.stg.agglomeration.br_geo_node.agglomeration_op_manager_link.table import \
            WrkAgglomerationDimBrGeoNodeOperationalManager
        from taxi_etl.layer.greenplum.stg.dbtaxi.agglomerations.agglomeration_reg_manager_link.table import \
            WrkDbtaxiDimGeoNodeRegionalManager
        from taxi_etl.layer.greenplum.stg.agglomeration.br_geo_node.agglomeration_reg_manager_link.table import \
            WrkAgglomerationDimBrGeoNodeRegionalManager
        from taxi_etl.layer.greenplum.cdm.geo.views.views import VDimFiGeoHierarchy
        from taxi_etl.layer.greenplum.cdm.geo.views.views import VDimFullGeoHierarchy
        from taxi_etl.layer.greenplum.cdm.geo.views.views import VDimOpGeoHierarchy
        from taxi_etl.layer.greenplum.cdm.marketplace.fct_order.views.fct_order_metric.table import FctOrderMetric

        gp_blacklist = {
            DmAmrGeoNodeAdditiveBase,
            AggTariffZoneSHMetricBase,
            AggTariffZoneSubsidyMetricBase,
            AggTariffZoneTariffClassCandidateMetricBase,
            DmAmrGeoNodeSHBase,
            DmAmrGeoNodeBase,
            AggTariffZoneMetricBase,
            AggTariffZoneTariffClassDlosMetricBase,
            WrkDbtaxiDimGeoNodeOperationalManager,
            WrkAgglomerationDimBrGeoNodeOperationalManager,
            WrkDbtaxiDimGeoNodeRegionalManager,
            WrkAgglomerationDimBrGeoNodeRegionalManager,
            VDimFiGeoHierarchy,
            VDimFullGeoHierarchy,
            VDimOpGeoHierarchy,
            FctOrderMetric
        }

    tables = set(
        inspect_utils.find_tables(
            module=etl_service.name,
            table_base_classes=(GPTable, ),
            table_blacklist=ABSTRACT_TABLE_LIST | gp_blacklist
        )
    )

    layout_to_tables = defaultdict(list)

    # Скипаем классы с некорректными и пустыми лэйаутами
    # Это могут быть базовые классы, тогда мы проверим их наследников
    for table in tables:
        try:
            table_layout = table.get_layout()  # type: ignore
            if table_layout is None:
                continue
        except:
            continue

        if table_layout is not None:
            layout_to_tables[table_layout].append(table)

    errors = []
    for lst in layout_to_tables.values():
        if len(lst) > 1:
            errors.append(tuple(lst))

    if errors:
        raise AssertionError(
            'These tables do not have a unique layout:\n' +
            ';\n'.join(map(str, errors))
        )


@base_workflow_checks
def check_all_tasks_have_valid_name(etl_service):
    regex = re.compile(r'[^a-zA-z0-9\-_]')

    # Найдём все таски
    task_bounds = collect_tasks(etl_service.name)
    tasks = [tb.task for tb in task_bounds]

    for task in tasks:
        assert regex.search(task.name) is None


class SelfTriggeringError(RuntimeError):
    pass


def check_self_triggering_loops(root_task, search_for_table):
    def recur(current_task):
        for table in current_task.get_targets():
            if table is search_for_table:
                if current_task is root_task:
                    raise SelfTriggeringError(
                        f'Таблица {search_for_table}\n'
                        f'создается реактивным таском {current_task}\n'
                        f'и при этом он может триггерится,\n'
                        f'ещё раз.'
                    )
                else:
                    raise SelfTriggeringError(
                        f'Таблица {search_for_table}\n'
                        f'создается таском {current_task}\n'
                        f'и триггерит граф {root_task},\n'
                        f'что может снова привести к изменению этой таблицы.\n'
                        f'и срабатываниям графа "по кругу".'
                    )
        for requirement_task in current_task.get_required_tasks():
            recur(requirement_task)
    recur(root_task)


@base_workflow_checks
def check_reactive_anomalies(etl_service):
    # Эта функция проверяет, что в сервисе нет реактивных
    # тасок, которые генерируют таблицы, на изменения которых
    # триггерятся сами.

    description = """
    Если такая ситуация происходит,
    то возникает потенциально бесконечный цикл. Обычно
    это может случится, когда вы делаете граф типа такого:

    Root -> Child

    1. Таска Child запускается по крону
    2. Генерит таблицу от которой зависит Root
    3. Граф Root Запускается реактивно, выполняет Child, Root и
       в результате снова обновляется таблица от которой зависит Root
    4. Реактивность снова запускает граф, переходя к шагу 3
       и образуется цикл – граф триггерит сам себя и расписание уже
       не участвует в запусках.

    Q: Почему это проблема?
    A: Потому что эти неконтролируемые запуски могут расходовать
       ресурсы, хотя мы не планировали запускать таск так часто.

    Q: Как же быть?
    A: Возможны два варианта:
       1. Перенести расписание с таска Child на Root,
          а Root сделать нереактивным. Так все вычисления
          будут выполняться с контролируемым интервалом.
       2. Убрать зависимость Root от Child, чтобы он перестал быть графом.
          Тогда Child будет запускаться по расписанию, а Root
          только тогда, когда обновились данные. В этом случае
          реактивный запуск Root уже не будет приводить к выполнению Child,
          и цикла возникать не будет."""
    bounds = collect_tasks(etl_service.name)
    errors = []

    for bound in bounds:
        task = bound.task
        if isinstance(task.scheduler, Trigger) \
           and not task.scheduler.recursive_is_ok:
            for entity, params in task.scheduler.parameters():
                try:
                    check_self_triggering_loops(task, entity)
                except SelfTriggeringError as e:
                    errors.append(e)

    if errors:
        err_as_str = '\n'.join(map(str, errors))
        raise AssertionError(f'{err_as_str}\n\n{dedent(description)}')


CONFIG_EXTENSIONS_WHITELIST = ['yaml']
CONFIG_FILENAMES_WHITELIST = [
    # особое исключение для spark:
    'log4j.properties'
]


def valid_config_file(file_path: pathlib.Path):
    return (
        file_path.is_file()
        and (
            file_path.suffix.lstrip('.') in CONFIG_EXTENSIONS_WHITELIST
            or file_path.name in CONFIG_FILENAMES_WHITELIST
        )
    )


def assert_config_extensions(config_dir: pathlib.Path):
    invalid_files = set()
    envs = ['default'] + list(Environment._SUPPORTED_ENVIRONMENTS)
    for env_name in envs:
        env_dir = config_dir / env_name
        if env_dir.exists():
            invalid_files.update(
                f for f in env_dir.iterdir()
                if not valid_config_file(f)
            )

    msg = f'Invalid config files: ' + ', '.join(str(f) for f in invalid_files)
    assert not invalid_files, msg


@base_workflow_checks
def check_service_config_extensions(etl_service):
    # etl сервисы проверяют только свои сервисные конфиги
    # общие конфиги проверяет dmp_suite
    config_dir = pathlib.Path(etl_service.home_dir, 'config_service')
    assert_config_extensions(config_dir)


@base_workflow_checks
def check_all_tasks_have_at_least_one_lock_provider(etl_service):
    task_bounds = collect_tasks(etl_service.name)

    for task_bound in task_bounds:
        task = task_bound.task
        assert len(task.get_lock_providers()) > 0
