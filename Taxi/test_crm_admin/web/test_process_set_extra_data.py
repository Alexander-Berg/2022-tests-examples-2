# pylint: disable=unused-variable

import aiohttp
import pytest

from crm_admin import storage


CSV = """

 name_ru ,extra_1, extra_2


Азербайджан, val_1_1, val_1_2
Баку, val_2_1, val_2_2

Благовещенск, val_3_1, val_3_2
Бобруйск, val_4_1, val_4_2
Брянская область, val_5_1, val_5_2
Кот-д'Ивуар, val_6_1, val_6_2
"Череповец", val_7_1, val_7_2

"""

CSV_ERROR_LINE = """
name_ru,extra_1, extra_2
Азербайджан, val_1_1
Баку, val_2_1, val_2_2"""

CSV_LOW_LINES = """
name_ru,extra_1, extra_2
Азербайджан, val_1_1, val_1_2
Баку, val_2_1, val_2_2"""


async def _exec_default_test_request(web_app_client, campaign_id=1, csv=CSV):
    form = aiohttp.FormData()
    form.add_field(name='file', value=csv, filename='test_audio.mp3')
    return await web_app_client.post(
        f'/v1/process/extra_data/csv?id={campaign_id}', data=form,
    )


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_without_file(web_app_client):
    form = aiohttp.FormData()
    form.add_field(name='file', value='', filename='')
    response = await web_app_client.post(
        f'/v1/process/extra_data/csv?id=1', data=form,
    )
    assert response.status == 404
    result = await response.json()
    assert result == {'message': 'File not found.'}


async def test_campaign_not_found(web_app_client):
    response = await _exec_default_test_request(web_app_client, -1)
    assert response.status == 404
    result = await response.json()
    assert result == {'message': 'Campaign -1 was not found'}


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_campaign_segment_is_empty(web_app_client):
    # Campaign_4.segment is None
    response = await _exec_default_test_request(web_app_client, 5)
    assert response.status == 404
    result = await response.json()
    assert result == {'message': 'Campaign 5 does not have segment.'}


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_segment_yt_is_empty(web_app_client):
    # segment_2.yt_table is None
    response = await _exec_default_test_request(web_app_client, 2)
    assert response.status == 404
    result = await response.json()
    assert result == {'message': 'Segment 2 does not have yt_table.'}


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_empty_file(web_app_client):
    response = await _exec_default_test_request(web_app_client, 1, '')
    assert response.status == 404
    result = await response.json()
    assert result == {'message': 'File is empty.'}


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_bad_delimiter(web_app_client):
    response = await _exec_default_test_request(
        web_app_client, 1, '' '' '' 'city    ext',
    )
    assert response.status == 404
    result = await response.json()
    assert result['message'].startswith(
        'The field separator must be "," or ";"',
    )


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_no_data_header_only(web_app_client, patch):
    @patch('crm_admin.api.process_set_extra_data.load_column_data')
    async def load_column_data(*args, **kwargs):
        pass

    response = await _exec_default_test_request(web_app_client, 1, 'city,ext')
    assert response.status == 424
    result = await response.json()
    assert result == {'message': 'empty csv file'}


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_success(web_context, web_app_client, patch):
    @patch('crm_admin.api.process_set_extra_data.load_column_data')
    async def load_column_data(*args, **kwargs):
        return {
            'Азербайджан',
            'Баку',
            'Благовещенск',
            'Бобруйск',
            'Брянская область',
            'Кот-д\'Ивуар',
            'Череповец',
        }

    @patch(
        'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.write_table',
    )
    async def write_table(*args, **kwargs):
        pass

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def exists(*args, **kwargs):
        return True

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.remove')
    async def remove(*args, **kwargs):
        pass

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.create')
    async def create(*args, **kwargs):
        pass

    @patch('crm_admin.utils.validation.groupings.extra_data_upload_validation')
    async def validate(*args, **kwargs):
        return []

    campaign_id = 1
    response = await _exec_default_test_request(web_app_client, campaign_id)
    assert response.status == 200

    assert write_table.calls
    assert exists.calls
    assert remove.calls
    assert create.calls

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.extra_data_path.endswith('/cmp_1_extra_data')
