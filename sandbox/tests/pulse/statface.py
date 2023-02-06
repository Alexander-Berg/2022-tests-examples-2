from datetime import datetime
from collections import OrderedDict

from sandbox.projects.sandbox_ci.pulse.statface import PulseShooterStatfaceData, PulseStaticStatfaceData


class TestsPulseShooterStatface(object):
    def test_get_rows_for_statface(self, diff_fixture):
        current_datetime = datetime.now()
        formatted_current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

        expect = [
            {"platform": "desktop", "percentile": "25", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "non_entry_name1": 0, "chunk_type": "base", "fielddate": formatted_current_datetime},
            {"platform": "desktop", "percentile": "50", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "non_entry_name1": 0, "chunk_type": "base", "fielddate": formatted_current_datetime},
            {"platform": "desktop", "percentile": "75", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "fielddate": formatted_current_datetime, "chunk_type": "base"},
            {"platform": "desktop", "percentile": "95", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "non_entry_name1": 0, "chunk_type": "base", "fielddate": formatted_current_datetime},
            {"platform": "desktop", "percentile": "99", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "non_entry_name1": 0, "chunk_type": "base", "fielddate": formatted_current_datetime},
            {"platform": "desktop", "percentile": "25", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "non_entry_name1": 1, "chunk_type": "actual", "fielddate": formatted_current_datetime},
            {"platform": "desktop", "percentile": "50", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "non_entry_name1": 1, "chunk_type": "actual", "fielddate": formatted_current_datetime},
            {"platform": "desktop", "percentile": "75", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "fielddate": formatted_current_datetime, "chunk_type": "actual"},
            {"platform": "desktop", "percentile": "95", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "non_entry_name1": 1, "chunk_type": "actual", "fielddate": formatted_current_datetime},
            {"platform": "desktop", "percentile": "99", "task_id": 1, "components": "RR:1; RR_CFG:1; PLAN:1",
             "non_entry_name1": 1, "chunk_type": "actual", "fielddate": formatted_current_datetime}
        ]

        statface_data = PulseShooterStatfaceData(
            current_datetime=current_datetime,
            report_data=diff_fixture,
            components=OrderedDict((
                ('RR', 1),
                ('RR_CFG', 1),
                ('PLAN', 1),
            )),
            platform='desktop',
            task_id=1,
        )
        actual = statface_data.get_rows_for_statface()

        assert actual == expect, 'Should reformat diff data to statface format'


class TestPulseStaticStatfaceData(object):
    def test_get_rows_for_statface(self, static_files_fixture):
        current_datetime = datetime.now()
        formatted_current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

        expect = [
            {
                'fielddate': formatted_current_datetime,
                'filename': '_common.header.pre.css',
                'platform': 'images-touch-pad',
                'size': 0,
                'task_id': 1,
            },
            {
                'fielddate': formatted_current_datetime,
                'filename': '_common.pre.css',
                'platform': 'images-touch-pad',
                'size': 4.09,
                'task_id': 1
            },
        ]

        statface_data = PulseStaticStatfaceData(current_datetime, static_files_fixture, 1)
        actual = statface_data.get_rows_for_statface()

        assert actual == expect, 'Should reformat reformat files data to statface format'
