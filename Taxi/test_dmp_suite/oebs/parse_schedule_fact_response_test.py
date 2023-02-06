import pytest

from dmp_suite.http.session_utils import SessionWithRetries
from dmp_suite.oebs import oebs_api


@pytest.mark.parametrize(
    'records, expected_result',
    [
        pytest.param(
            [
                {
                    "assignments": [
                        {
                            "EmpName": "aleks",
                            "Transferted": 'Y',
                            "TypeOperations": [
                                {
                                    "OperationCreationLogin": "creator1",
                                    "OperationsCreationDate": "2021-12-29 23:26:25",
                                    "OperationsEndDate": "2021-12-01 00:00",
                                    "OperationsId": 1,
                                    "OperationsStartDate": "2021-12-01 00:00",
                                    "OperationsTime": "05:00",
                                    "TypeOperation": "B"
                                },
                                {
                                    "OperationCreationLogin": "creator1",
                                    "OperationsCreationDate": "2021-12-29 23:26:25",
                                    "OperationsEndDate": "2021-12-02 00:00",
                                    "OperationsId": 1,
                                    "OperationsStartDate": "2021-12-02 00:00",
                                    "OperationsTime": "06:00",
                                    "TypeOperation": "A"
                                }
                            ],
                            "assignmentNumber": "assign1",
                            "orgID": 10,
                            "orgName": "org1"
                        }
                    ],
                    "login": "login1"
                },
                {
                    "assignments": [
                        {
                            "EmpName": "michael",
                            "Transferted": 'N',
                            "TypeOperations": [
                                {
                                    "OperationCreationLogin": "creator2",
                                    "OperationsCreationDate": "2021-12-20 23:26:25",
                                    "OperationsEndDate": "2021-11-01 00:00",
                                    "OperationsId": 2,
                                    "OperationsStartDate": "2021-11-01 00:00",
                                    "OperationsTime": "03:00",
                                    "TypeOperation": "A"
                                },
                            ],
                            "assignmentNumber": "assign2",
                            "orgID": 20,
                            "orgName": "org2"
                        }
                    ],
                    "login": "login2"
                },
                {
                    "assignments": [
                        {
                            "message": "Не найден логин сотрудника с 2021-12-01 по 2022-01-01"
                        }
                    ],
                    "login": "login3"
                }
            ],
            [
                {
                    "EmpName": "aleks",
                    "OperationCreationLogin": "creator1",
                    "OperationsCreationDate": "2021-12-29 23:26:25",
                    "OperationsEndDate": "2021-12-01 00:00",
                    "OperationsId": 1,
                    "OperationsStartDate": "2021-12-01 00:00",
                    "OperationsTime": "05:00",
                    "Transferted": "Y",
                    "TypeOperation": "B",
                    "assignmentNumber": "assign1",
                    "login": "login1",
                    "orgID": 10,
                    "orgName": "org1"
                },
                {
                    "EmpName": "aleks",
                    "OperationCreationLogin": "creator1",
                    "OperationsCreationDate": "2021-12-29 23:26:25",
                    "OperationsEndDate": "2021-12-02 00:00",
                    "OperationsId": 1,
                    "OperationsStartDate": "2021-12-02 00:00",
                    "OperationsTime": "06:00",
                    "Transferted": "Y",
                    "TypeOperation": "A",
                    "assignmentNumber": "assign1",
                    "login": "login1",
                    "orgID": 10,
                    "orgName": "org1"
                },
                {
                    "EmpName": "michael",
                    "OperationCreationLogin": "creator2",
                    "OperationsCreationDate": "2021-12-20 23:26:25",
                    "OperationsEndDate": "2021-11-01 00:00",
                    "OperationsId": 2,
                    "OperationsStartDate": "2021-11-01 00:00",
                    "OperationsTime": "03:00",
                    "Transferted": "N",
                    "TypeOperation": "A",
                    "assignmentNumber": "assign2",
                    "login": "login2",
                    "orgID": 20,
                    "orgName": "org2"
                }
            ],
            id='basic test'
        ),
        ]
    )
def test_parse_schedule_fact_response(records, expected_result):
    api = oebs_api.ApiWrapper(SessionWithRetries(), 'base_url')
    actual_result = api.parse_schedule_fact_response(records)
    for actual, expected in zip(actual_result, expected_result):
        assert actual == expected
