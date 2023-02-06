from dashboards.internal.models import configs_upload


async def test_enqueue_dashboard_config_upload(call_cube, web_context):
    response = await call_cube(
        'EnqueueDashboardConfigUpload',
        {
            'diff_proposal': {
                'base': 'master',
                'changes': [
                    {
                        'data': 'content1',
                        'filepath': (
                            'dorblu/taxi/nanny.taxi_clownductor_stable.yaml'
                        ),
                        'state': 'created_or_updated',
                    },
                    {
                        'data': 'content2',
                        'filepath': (
                            'grafana/nanny_taxi_clownductor_stable.yaml'
                        ),
                        'state': 'created_or_updated',
                    },
                ],
                'comment': 'Update dashboard configs',
                'repo': 'infra-cfg-graphs',
                'title': (
                    'feat clownductor: update dashboard configs in stable'
                ),
                'user': 'taxi',
            },
        },
    )
    assert response['status'] == 'success'
    assert response['payload'] == {'config_upload_ids': [1, 2]}
    db_manager = configs_upload.ConfigsUploadManager(web_context)
    result = await db_manager.fetch()
    result_map = {}
    for record in result:
        assert record.status == configs_upload.ConfigUploadStatus.WAITING
        assert not record.job_idempotency_key
        result_map[record.id] = {
            'vendor': record.vendor,
            'content': record.content,
            'filepath': record.filepath,
        }
    expected = {
        1: {
            'content': 'content1',
            'filepath': 'dorblu/taxi/nanny.taxi_clownductor_stable.yaml',
            'vendor': configs_upload.ConfigUploadVendor.ARCADIA,
        },
        2: {
            'content': 'content2',
            'filepath': 'grafana/nanny_taxi_clownductor_stable.yaml',
            'vendor': configs_upload.ConfigUploadVendor.ARCADIA,
        },
    }
    assert expected == result_map
