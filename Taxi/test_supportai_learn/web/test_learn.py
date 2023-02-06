import pytest


@pytest.mark.pgsql('supportai_learn', files=['learn_results.sql'])
async def test_get_learn_results(web_app_client, patch, load_binary):
    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(*args, **kwargs):
        return load_binary('learn_results.json')

    response = await web_app_client.get(
        '/v1/learn/1/results?user_id=34&project_slug=test',
    )

    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['metrics']['topics']) == 3

    assert response_json['s3_path'] == 'learn/1234'
    assert response_json['metrics']['accuracy'] == 0.5
