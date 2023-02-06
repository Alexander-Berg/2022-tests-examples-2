import pytest

import metrika.admin.python.cms.lib.fsm.states as cms_fsm

testdata_success = [
    # "автоматическая" ветвь - через reject
    pytest.param(cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, cms_fsm.States.REJECT_WAIT_FOR_WALLE_DELETE, False),
    pytest.param(cms_fsm.States.REJECT_WAIT_FOR_WALLE_DELETE, cms_fsm.States.COMPLETED, True),

    # "автоматическая" ветвь - через ok
    pytest.param(cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD, cms_fsm.States.UNLOADING, False),
    pytest.param(cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_OK, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, False),
    pytest.param(cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, cms_fsm.States.INITIATE_LOADING, True),
    pytest.param(cms_fsm.States.INITIATE_LOADING, cms_fsm.States.WAIT_FOR_LOADING_COMPLETE, True),
    pytest.param(cms_fsm.States.WAIT_FOR_LOADING_COMPLETE, cms_fsm.States.FINALIZE_LOADING, True),
    pytest.param(cms_fsm.States.FINALIZE_LOADING, cms_fsm.States.COMPLETED, True),

    # Хост в Wall-E Не помечен как READY
    pytest.param(cms_fsm.States.INITIATE_LOADING, cms_fsm.States.COMPLETED, True),

    # "ручное решение"
    pytest.param(cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, cms_fsm.States.REJECT_WAIT_FOR_WALLE_DELETE, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, False),

    # "fallback на ручное решение"
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_OK, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, False),

    # "не удалось вывести из работы"
    pytest.param(cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, False),

    # "не удалсь ввести в работу"
    pytest.param(cms_fsm.States.INITIATE_LOADING, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.WAIT_FOR_LOADING_COMPLETE, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.FINALIZE_LOADING, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.COMPLETED, True),

    # "Wall-E удаляет задачу в in-process" - попадаем в WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD из которого только в COMPLETED
    pytest.param(cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_OK, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
]

testdata_fail = [
    # раньше было можно
    pytest.param(cms_fsm.States.MAKING_DECISION, cms_fsm.States.UNLOADING, False),

    # сам в себя - нельзя
    pytest.param(cms_fsm.States.MAKING_DECISION, cms_fsm.States.MAKING_DECISION, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_OK, cms_fsm.States.WAIT_FOR_APPROVAL_OK, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, False),
    pytest.param(cms_fsm.States.REJECT_WAIT_FOR_WALLE_DELETE, cms_fsm.States.REJECT_WAIT_FOR_WALLE_DELETE, False),
    pytest.param(cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, False),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
    pytest.param(cms_fsm.States.WAIT_FOR_LOADING_COMPLETE, cms_fsm.States.WAIT_FOR_LOADING_COMPLETE, True),
    pytest.param(cms_fsm.States.FINALIZE_LOADING, cms_fsm.States.FINALIZE_LOADING, True),
    pytest.param(cms_fsm.States.UNLOADING, cms_fsm.States.UNLOADING, False),
    pytest.param(cms_fsm.States.INITIATE_LOADING, cms_fsm.States.INITIATE_LOADING, True),

    # из финального - никуда
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.MAKING_DECISION, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.UNLOADING, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.WAIT_FOR_APPROVAL_OK, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.REJECT_WAIT_FOR_WALLE_DELETE, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.INITIATE_LOADING, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.WAIT_FOR_LOADING_COMPLETE, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.FINALIZE_LOADING, True),
    pytest.param(cms_fsm.States.COMPLETED, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, True),
]

testdata_unexpected = [
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.MAKING_DECISION, cms_fsm.States.UNLOADING, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, True),

    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.WAIT_FOR_APPROVAL_REJECT, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, True),
    pytest.param(cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.WAIT_FOR_APPROVAL_OK, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, True),
]

testdata_invalid = [
    pytest.param(cms_fsm.States.LOADING, cms_fsm.States.LOADING, cms_fsm.States.COMPLETED, True)
]

testdata_audit_positive = [
    pytest.param("subject", True, "Some action was performed", "Operation successfull", {}),
    pytest.param("subject", True, "Some action was performed", "Operation successfull", {"details": {"key": "value"}}),
    pytest.param("subject", False, "Some action was performed", "Reason of failure", {}),
    pytest.param("subject", False, "Some action was performed", "Reason of failure", {"details": {"key": "value"}}),
]

testdata_audit_negative = [
    # Должен быть субъект действия
    pytest.param(None, True, "Some action was performed", None, {}),
    # Должно быть сообщение аудита
    pytest.param("subject", True, None, None, {}),
    # Должна быть причина отсутствия упеха
    pytest.param("subject", False, "Some action was performed", None, {}),
]
