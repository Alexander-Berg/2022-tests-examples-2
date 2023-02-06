import copy
import typing

import pytest
from unittest import TestCase
from unittest.mock import patch, Mock

import l3manager_agent


MOCKED_AGENT_RESPONSE = {
    "exceptions": {"CommandExecutionError": 0},
    "executions": {"collect_settings": 0.026},
    "transitions": {"IDLE<->WAITING": 0.026, "WAITING<->WAITING": 3.825, "WAITING<->IDLE": 0.0},
    "tvm": {"tvm_enabled": 0, "tvm_alive": 0, "tvm_current_status": 0},
    "errors": 0,
    "created_at": 1652952060.3251328,
    "updated_at": 1652953523.0798328,
}

# current time should be bigger that created + critical TTL for successful created_at validation.
CURRENT_TIME = MOCKED_AGENT_RESPONSE["created_at"] + l3manager_agent.CRITICAL_CREATED_AT_SEC + 1


def mocked_requests_json(payload: typing.Dict[str, typing.Any] = MOCKED_AGENT_RESPONSE) -> Mock:
    response = Mock()
    response.json = Mock(return_value=payload)

    return response


class TestL3managerAgent(TestCase):
    @patch("time.time", return_value=CURRENT_TIME)
    @patch("requests.get")
    def test_successfil(self, mocked_get, *_):
        mocked_get.return_value = mocked_requests_json()
        l3manager_agent.main()

    @patch("time.time", return_value=MOCKED_AGENT_RESPONSE["created_at"] + l3manager_agent.CRITICAL_CREATED_AT_SEC - 1)
    @patch("requests.get")
    def test_fail_created_at(self, mocked_get, *_):
        mocked_get.return_value = mocked_requests_json()

        with pytest.raises(RuntimeError) as err:
            l3manager_agent.main()
        assert "agent was started less than" in str(err.value)

    @patch("time.time", return_value=CURRENT_TIME)
    @patch("requests.get")
    def test_fail_updated_at(self, mocked_get, *_):
        payload = copy.deepcopy(MOCKED_AGENT_RESPONSE)
        payload["updated_at"] = CURRENT_TIME - l3manager_agent.CRITICAL_IDLE_SEC - 1
        mocked_get.return_value = mocked_requests_json(payload)

        with pytest.raises(RuntimeError) as err:
            l3manager_agent.main()
        assert "agent was not update states last" in str(err.value)

    @patch("time.time", return_value=CURRENT_TIME)
    @patch("requests.get")
    def test_fail_tvm(self, mocked_get, *_):
        payload = copy.deepcopy(MOCKED_AGENT_RESPONSE)
        payload["tvm"]["tvm_alive"] = 2
        print(payload)
        mocked_get.return_value = mocked_requests_json(payload)

        with pytest.raises(ValueError) as err:
            l3manager_agent.main()
        assert "TVM auth is not alive" in str(err.value)

    @patch("time.time", return_value=CURRENT_TIME)
    @patch("requests.get")
    def test_fail_errors(self, mocked_get, *_):
        payload = copy.deepcopy(MOCKED_AGENT_RESPONSE)
        payload["errors"] = 1
        mocked_get.return_value = mocked_requests_json(payload)

        with pytest.raises(ValueError) as err:
            l3manager_agent.main()
        assert "agents contains errors" in str(err.value)

    @patch("time.time", return_value=CURRENT_TIME)
    @patch("requests.get")
    def test_fail_exceptions(self, mocked_get, *_):
        payload = copy.deepcopy(MOCKED_AGENT_RESPONSE)
        payload["exceptions"].update({"CommandExecutionError": 1})
        mocked_get.return_value = mocked_requests_json(payload)

        with pytest.raises(ValueError) as err:
            l3manager_agent.main()
        assert "agents contains errors" in str(err.value)
