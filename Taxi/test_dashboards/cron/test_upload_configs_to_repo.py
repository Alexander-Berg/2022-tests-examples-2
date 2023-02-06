import pytest

from testsuite.utils import matching

from dashboards.internal.models import configs_upload


class MockTpContext:
    def __init__(self):
        self._existed_jobs = {
            'key1': self._fill_data(1, 'success', 'arcadia', {}, 'key1'),
            'key4': self._fill_data(3, 'success', 'arcadia', {}, 'key4'),
        }
        self._last_id = 2

    def jobs_count(self):
        return len(self._existed_jobs)

    @staticmethod
    def _fill_data(job_id, status, job_name, job_vars, change_doc_id):
        return {
            'id': job_id,
            'status': status,
            'recipe_id': 1,
            'name': job_name,
            'created_at': 1,
            'job_vars': job_vars,
            'change_doc_id': change_doc_id,
        }

    def exists(self, change_doc_id):
        return change_doc_id in self._existed_jobs

    def add(self, body):
        self._last_id += 1
        change_doc_id = body['change_doc_id']
        self._existed_jobs[change_doc_id] = self._fill_data(
            self._last_id,
            'in_progress',
            body['recipe_name'],
            body['job_vars'],
            change_doc_id,
        )

    def get(self, change_doc_id):
        return self._existed_jobs[change_doc_id]


@pytest.fixture(name='mock_tp_context')
def _mock_tp_context():
    return MockTpContext()


@pytest.fixture(name='mock_tp')
def _mock_tp(mockserver, mock_tp_context):
    class Mocks:
        @staticmethod
        @mockserver.json_handler(
            '/task-processor/v1/jobs/retrieve_by_change_doc_id/',
        )
        async def _retrieve_by_change_doc_id(request):
            if mock_tp_context.exists(request.json['change_doc_id']):
                job = mock_tp_context.get(request.json['change_doc_id'])
                return {'jobs': [job]}
            return mockserver.make_response(json={}, status=404)

        @staticmethod
        @mockserver.json_handler('/task-processor/v1/jobs/start/')
        async def _start(request):
            mock_tp_context.add(request.json)
            return {
                'job_id': mock_tp_context.get(request.json['change_doc_id'])[
                    'id'
                ],
            }

    return Mocks()


@pytest.mark.pgsql('dashboards', files=['init_data.sql'])
async def test_upload_configs_to_repo(
        mock_tp, cron_runner, cron_context, mock_tp_context,
):
    await cron_runner.upload_configs_to_repo()
    db_manager = configs_upload.ConfigsUploadManager(cron_context)
    all_records = await db_manager.fetch(status=None, vendor=None)
    all_records_map = {
        record.id: {
            'status': record.status.value,
            'job_idempotency_key': record.job_idempotency_key,
        }
        for record in all_records
    }
    expected_records = {
        1: {'status': 'applied', 'job_idempotency_key': 'key1'},
        2: {'status': 'applying', 'job_idempotency_key': matching.uuid_string},
        3: {'status': 'applying', 'job_idempotency_key': 'key2'},
        4: {'status': 'applying', 'job_idempotency_key': 'key2'},
        5: {'status': 'applied', 'job_idempotency_key': 'key4'},
        6: {'status': 'applied', 'job_idempotency_key': 'key4'},
    }
    assert expected_records == all_records_map

    all_idempotency_keys = {
        record.job_idempotency_key for record in all_records
    }
    assert len(all_idempotency_keys) == 4
    assert mock_tp_context.jobs_count() == 4
    new_key = next(iter(all_idempotency_keys - {'key1', 'key2', 'key4'}))
    key2_job = mock_tp_context.get('key2')
    assert key2_job['status'] == 'in_progress'
    changes = key2_job['job_vars']['diff_proposal'].pop('changes')
    assert sorted(changes, key=lambda x: x['filepath']) == [
        {
            'filepath': 'filepath2',
            'state': 'created_or_updated',
            'data': 'content2',
        },
        {
            'filepath': 'filepath3',
            'state': 'created_or_updated',
            'data': 'content3',
        },
    ]
    assert key2_job['job_vars'] == {
        'diff_proposal': {
            'user': 'arcadia',
            'repo': 'taxi/infra-cfg-graphs',
            'title': 'Update dashboard configs',
            'base': 'trunk',
            'comment': 'Update grafana and dorblu configs. (Token: key2)',
        },
        'st_ticket': None,
        'reviewers': None,
        'automerge': True,
        'approve_required': False,
        'robot_for_ship': None,
    }
    assert key2_job['name'] == 'ArcadiaMergeDiffProposalWithPR'

    new_job = mock_tp_context.get(new_key)
    assert new_job['status'] == 'in_progress'
    assert new_job['job_vars'] == {
        'diff_proposal': {
            'base': 'trunk',
            'changes': [
                {
                    'data': 'content4',
                    'filepath': 'filepath4',
                    'state': 'created_or_updated',
                },
            ],
            'comment': (
                f'Update grafana and dorblu configs. (Token: {new_key})'
            ),
            'repo': 'taxi/infra-cfg-graphs',
            'title': 'Update dashboard configs',
            'user': 'arcadia',
        },
        'st_ticket': None,
        'reviewers': None,
        'automerge': True,
        'approve_required': False,
        'robot_for_ship': None,
    }
    assert new_job['name'] == 'ArcadiaMergeDiffProposalWithPR'
