import pytest
from unittest import mock

from connection.yql import add_annotations
from dmp_suite.exceptions import DWHError
from init_py_env import service


environ = {
    'TAXIDWH_TASK': 'test',
    'TAXIDWH_RUN_ID': '97531'
}


query0 = """
select 0;
"""
annotated_query0 = f"""
pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 0;
"""

query1 = """
PRAGMA yt.OperationSpec =  '{}';

select 1;
"""
annotated_query1 = f"""
pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 1;
"""

query2 = """
pragma  yt.OperationSpec = '{"cpu" = 30}';

select 2;
"""
annotated_query2 = f"""
pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

pragma yt.OperationSpec = '{{"cpu" = 30; "annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 2;
"""

query3 = """
PRAGMA yt.OperationSpec =  '{"cpu" = 80; "mem" = 100}';

select 3;
"""
annotated_query3 = f"""
pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

pragma yt.OperationSpec = '{{"cpu" = 80; "mem" = 100; "annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 3;
"""

query4 = """
prAGmA yt.OperationSpec =  '{"cpu" = 70; "l1" = {"l2" = {"l3" = {"k1" = "v1"; "k2" = "v2"}}}; "mem" = 50}';

select 4;
"""
annotated_query4 = f"""
pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

pragma yt.OperationSpec = '{{"cpu" = 70; "l1" = {{"l2" = {{"l3" = {{"k1" = "v1"; "k2" = "v2"}}}}}}; "mem" = 50; "annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 4;
"""

query5 = """
use hahn;
PRAGMA yt.OperationSpec = '{"k1" = "v1"; 
                            "k2" = "v2"}';

select 5;
"""
annotated_query5 = f"""
pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

use hahn;
pragma yt.OperationSpec = '{{"k1" = "v1"; "k2" = "v2"; "annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 5;"""

query6 = """
select 60; pragma yt.OperationSpec = '{}'; select 61;
"""
annotated_query6 = f"""
pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 60; pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}'; select 61;
"""

query7 = """
select 70;

pragma  yt.OperationSpec = '{"cpu" = 10}';

select 71;

pragma  yt.OperationSpec = '{"cpu" = 20}';

select 72;

pragma  yt.OperationSpec = '{"cpu" = 30}';

select 73;
"""
annotated_query7 = f"""
pragma yt.OperationSpec = '{{"annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 70;

pragma yt.OperationSpec = '{{"cpu" = 10; "annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 71;

pragma yt.OperationSpec = '{{"cpu" = 20; "annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 72;

pragma yt.OperationSpec = '{{"cpu" = 30; "annotations" = {{"taxidmp_task" = "test"; "taxidmp_run_id" = "97531"; "backend_type" = "yql"; "task_service_code" = "{service.name}"}}}}';

select 73;
"""


@pytest.mark.parametrize("data", [
    (query0, annotated_query0),
    (query1, annotated_query1),
    (query2, annotated_query2),
    (query3, annotated_query3),
    (query4, annotated_query4),
    (query5, annotated_query5),
    (query6, annotated_query6),
    (query7, annotated_query7),
])
def test_add_annotations(data):
    query, annotated_query = data
    with mock.patch('os.environ', environ):
        assert add_annotations(query.strip()) == annotated_query.strip()


@pytest.mark.parametrize("query", [
    """pragma yt.OperationSpec = '{"k1" = "v1"; "k2" = "v2"; "hack'key" = "val"}'; select 1;""",
])
def test_add_annotations_error_msg(query):
    with pytest.raises(DWHError):
        with mock.patch('os.environ', environ):
            add_annotations(query)
