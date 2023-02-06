# pylint: disable=redefined-outer-name,unused-variable,too-many-lines
import dateutil.parser
import pytest
import pytz

from crm_admin import settings
from crm_admin import storage
from test_crm_admin.utils import audience_cfg

CRM_ADMIN_TEST_SETTINGS = {
    'NirvanaSettings': {
        'instance_id': '618c35c0-8a4d-4b61-9ebf-856d7359dfca',
        'workflow_id': '8bff6765-9fe2-484c-99a7-149cf2b90ac9',
        'workflow_retry_period': 60,
        'workflow_timeout': 3600,
    },
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'target_statuses': ['target_status'],
        'idea_approved_statuses': ['target_status'],
        'unapproved_statuses': ['В работе'],
    },
    **audience_cfg.CRM_ADMIN_SETTINGS,
}

CRM_ADMIN_GROUPS_V2 = {'campaigns': [1], 'all_on': False}


@pytest.fixture(autouse=True)
def skip_campaign_validation(patch):
    @patch(
        'crm_admin.utils.validation'
        '.campaign_validators.campaign_efficiency',
    )
    async def validation(*agrs, **kwargs):  # pylint: disable=unused-variable
        return []

    @patch(
        'crm_admin.utils.validation'
        '.campaign_validators.campaign_efficiency_stop_time',
    )
    async def e_validation(*agrs, **kwargs):  # pylint: disable=unused-variable
        return []


def parse_datetime(string):
    time = dateutil.parser.parse(string)
    return time.astimezone(pytz.utc).replace(tzinfo=None)


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.parametrize(
    'file,result', [('campaign_new.json', 201), ('campaign_empty.json', 400)],
)
async def test_create_campaign(
        web_app_client,
        load_json,
        is_campaign_exist,
        file,
        result,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    new_forms = load_json(file)
    for campaign, new_form in new_forms.items():
        owner = 'user_owner'
        response = await web_app_client.post(
            '/v1/campaigns/item',
            json=new_form,
            headers={'X-Yandex-Login': owner},
        )
        assert response.status == result
        if response.status == 201:
            response_data = await response.json()

            common_keys = response_data.keys() & new_form.keys()
            actual = {
                k: v for k, v in response_data.items() if k in common_keys
            }
            expected = {k: v for k, v in new_form.items() if k in common_keys}
            assert actual == expected

            new_campaign_id = response_data['id']
            assert is_campaign_exist(new_campaign_id, new_form, owner)


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.parametrize('campaign_type', ['oneshot', 'regular'])
@pytest.mark.parametrize('audience', ['User', 'Driver', 'EatsUser'])
async def test_create_campaign_by_audience(
        web_app_client,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        audience,
        campaign_type,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    params = {
        'campaign_type': campaign_type,
        'com_politic': True,
        'discount': True,
        'entity': audience,
        'global_control': True,
        'kind': 'kind',
        'name': 'name',
        'trend': 'trend',
    }
    owner = 'user'
    response = await web_app_client.post(
        '/v1/campaigns/item', json=params, headers={'X-Yandex-Login': owner},
    )
    assert response.status == 201

    campaign = await response.json()
    assert campaign['entity'] == audience
    assert campaign['campaign_type'] == campaign_type
    assert patch_issue.calls


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_create_campaign_default_salt(
        web_app_client,
        load_json,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    params = load_json('campaign_new.json')['campaign_1']
    del params['salt']

    response = await web_app_client.post(
        '/v1/campaigns/item', json=params, headers={'X-Yandex-Login': 'user'},
    )
    assert response.status == 201

    campaign = await response.json()
    assert campaign['salt'] is not None


@pytest.mark.parametrize(
    'file, id_, result',
    [
        ('campaign_current.json', 1, 200),
        ('campaign_current.json', 123, 200),
        ('', 100, 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_campaign(web_app_client, load_json, file, id_, result):
    response = await web_app_client.get(
        '/v1/campaigns/item', params={'id': id_},
    )
    assert response.status == result
    if response.status == 200:
        existing_campaign = load_json(file)
        retrieved_campaign = await response.json()
        assert retrieved_campaign in existing_campaign


@pytest.mark.pgsql('crm_admin', files=['deleted_campaign.sql'])
@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
async def test_retrieve_deleted_campaign(web_app_client):
    response = await web_app_client.get('/v1/campaigns/item', params={'id': 1})
    assert response.status == 400
    response_body = await response.json()
    assert response_body['errors'][0]['code'] == 'campaign_was_deleted'


@pytest.mark.config(
    CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2,
    CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS,
)
@pytest.mark.parametrize(
    'file, id_, result', [('campaign_current_2.json', 1, 200)],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
async def test_retrieve_campaign_v2(
        web_app_client, load_json, file, id_, result,
):
    response = await web_app_client.get(
        '/v1/campaigns/item', params={'id': id_},
    )
    assert response.status == result
    if response.status == 200:
        existing_campaign = load_json(file)
        retrieved_campaign = await response.json()
        assert existing_campaign == retrieved_campaign


@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
@pytest.mark.parametrize(
    'file, id_, result',
    [
        ('campaign_updated.json', 1, 200),
        ('campaign_updated.json', 123, 200),
        ('campaign_updated.json', 100, 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
async def test_update_campaign(
        web_app_client,
        load_json,
        is_campaign_exist,
        file,
        id_,
        result,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    forms = load_json(file)
    updated_form = forms.get(f'campaign_{id_}', forms['campaign_1'])

    ticket = updated_form['ticket']
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + f'issues/{ticket}/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    response = await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': id_},
        json=updated_form,
        headers={'X-Yandex-Login': 'user_owner'},
    )
    assert response.status == result
    if response.status == 200:
        retrieved_campaign = await response.json()
        assert retrieved_campaign == updated_form
        assert is_campaign_exist(id_, updated_form)


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
async def test_update_campaign_in_wrong_state_fails(
        web_context,
        web_app_client,
        load_json,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    campaign_id = 1

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id=1)
    campaign.state = settings.SEGMENT_PROCESSING_STATE
    assert campaign.state not in settings.CAMPAIGN_EDITABLE_STATES
    await db_campaign.update_state(campaign)

    updated_form = load_json('campaign_updated.json')['campaign_1']

    ticket = updated_form['ticket']
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + f'issues/{ticket}/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    response = await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': campaign_id},
        json=updated_form,
        headers={'X-Yandex-Login': 'user_owner'},
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'global_control, com_politic',
    [(True, False), (False, True), (False, False)],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_update_campaign_restart(
        web_context,
        web_app_client,
        load_json,
        patch,
        global_control,
        com_politic,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    campaign_id = 9

    campaign_params = load_json('campaign_updated.json')['campaign_1']
    campaign_params['com_politic'] = com_politic
    campaign_params['global_control'] = global_control

    # initialize com_politic and global_control flags
    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.com_politic = False
    campaign.global_control = False
    campaign.salt = campaign_params['salt']
    await db_campaign.update(campaign)

    ticket = campaign_params['ticket']
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + f'issues/{ticket}/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    @patch('crm_admin.api.update_campaign.process_segment.start_task')
    async def start_task(*args, **kwargs):
        pass

    await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': campaign_id},
        json=campaign_params,
        headers={'X-Yandex-Login': 'user_owner'},
    )
    campaign = await db_campaign.fetch(campaign_id)

    if global_control or com_politic:
        assert start_task.calls
        assert campaign.state == settings.SEGMENT_PREPROCESSING_STATE
    else:
        assert not start_task.calls


@pytest.mark.parametrize(
    'campaign_id, status',
    [
        (1, 200),
        (2, 200),  # no nirvana tasks / shared groups
        (3, 404),  # no segment
    ],
)
@pytest.mark.pgsql('crm_admin', files=['campaign_log.sql'])
async def test_read_campaign_log(
        web_app_client, load_json, campaign_id, status,
):
    response = await web_app_client.get(
        '/v1/campaigns/log', params={'id': campaign_id},
    )

    assert response.status == status
    if status != 404:
        logs = load_json('campaign_logs.json')
        value = await response.json()
        assert value == logs[str(campaign_id)]


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_planned_start_date(
        web_context,
        web_app_client,
        load_json,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    # create campaign
    params = load_json('campaign_new.json')['campaign_1']
    params['planned_start_date'] = '2021-01-01'
    response = await web_app_client.post(
        '/v1/campaigns/item', json=params, headers={'X-Yandex-Login': 'user'},
    )
    assert response.status == 201

    campaign_id = (await response.json())['id']

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert str(campaign.planned_start_date) == params['planned_start_date']

    # update campaign
    params['planned_start_date'] = '2022-01-01'

    response = await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': campaign_id},
        json=params,
        headers={'X-Yandex-Login': 'user'},
    )
    assert response.status == 200

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert str(campaign.planned_start_date) == params['planned_start_date']

    # get campagin
    response = await web_app_client.get(
        '/v1/campaigns/item', params={'id': campaign_id},
    )
    assert response.status == 200
    response = await response.json()
    assert response['planned_start_date'] == params['planned_start_date']


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_reset_planned_start_date(
        web_context,
        web_app_client,
        load_json,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    # create campaign
    params = load_json('campaign_new.json')['campaign_1']
    params['planned_start_date'] = '2021-01-01'
    response = await web_app_client.post(
        '/v1/campaigns/item', json=params, headers={'X-Yandex-Login': 'user'},
    )
    assert response.status == 201

    # reset the planned date
    campaign_id = (await response.json())['id']
    del params['planned_start_date']

    response = await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': campaign_id},
        json=params,
        headers={'X-Yandex-Login': 'user'},
    )
    assert response.status == 200

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.planned_start_date is None


@pytest.mark.parametrize(
    'schedule,start_time,stop_time,status',
    [
        (
            '* */1 * * *',
            '2021-01-01T03:00:00+03:00',
            '2021-02-01T03:00:00+03:00',
            201,
        ),
        (
            '* */1 *',
            '2022-01-01T03:00:00+03:00',
            '2021-02-01T03:00:00+03:00',
            400,
        ),
        (None, '2022-01-01T03:00:00+03:00', '2021-02-01T03:00:00+03:00', 400),
        (
            '* */1 * * *',
            '2021-01-01T03:00:00+03:00',
            '2022-01-02T03:00:00+03:00',
            400,
        ),
    ],
)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_create_regular_campaign(
        web_context,
        web_app_client,
        load_json,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        schedule,
        start_time,
        stop_time,
        status,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    data = load_json('campaign_new.json')['campaign_1']
    data['campaign_type'] = 'regular'
    data['schedule'] = schedule
    data['regular_start_time'] = start_time
    data['regular_stop_time'] = stop_time

    response = await web_app_client.post(
        '/v1/campaigns/item', json=data, headers={'X-Yandex-Login': 'user'},
    )
    assert response.status == status

    if status == 201:
        response = await response.json()
        assert response['campaign_type'] == 'regular'
        assert response['schedule'] == data['schedule']
        assert response['regular_start_time'] == data['regular_start_time']
        assert response['regular_stop_time'] == data['regular_stop_time']

        campaign_id = response['id']
        db_campaign = storage.DbCampaign(web_context)
        campaign = await db_campaign.fetch(campaign_id)

        assert campaign.is_regular
        assert campaign.schedule == data['schedule']
        assert campaign.regular_start_time == parse_datetime(
            data['regular_start_time'],
        )
        assert campaign.regular_stop_time == parse_datetime(
            data['regular_stop_time'],
        )


@pytest.mark.parametrize(
    'schedule,status', [('*/10 */10 * * *', 200), ('* */1 *', 400)],
)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['regular_campaigns.sql'])
async def test_update_regular_campaign(
        web_context,
        web_app_client,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        schedule,
        status,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    campaign_id = 1001

    response = await web_app_client.get(
        '/v1/campaigns/item', params={'id': campaign_id},
    )
    data = await response.json()
    data['schedule'] = schedule
    data['regular_start_time'] = '2022-11-01T03:00:00+03:00'
    data['regular_stop_time'] = '2022-12-01T03:00:00+03:00'

    response = await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': campaign_id},
        json=data,
        headers={'X-Yandex-Login': 'user'},
    )
    assert response.status == status

    if status == 200:
        response = await response.json()
        assert response['campaign_type'] == 'regular'
        assert response['schedule'] == data['schedule']
        assert response['regular_start_time'] == data['regular_start_time']
        assert response['regular_stop_time'] == data['regular_stop_time']

        db_campaign = storage.DbCampaign(web_context)
        campaign = await db_campaign.fetch(response['id'])
        assert campaign.is_regular
        assert campaign.schedule == data['schedule']
        assert campaign.regular_start_time == parse_datetime(
            data['regular_start_time'],
        )
        assert campaign.regular_stop_time == parse_datetime(
            data['regular_stop_time'],
        )


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['regular_campaigns.sql'])
async def test_activate_regular_campaign(
        web_context,
        web_app_client,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    campaign_id = 1001

    response = await web_app_client.get(
        '/v1/campaigns/item', params={'id': campaign_id},
    )
    data = await response.json()
    assert data['campaign_type'] == 'regular'
    assert data.get('is_active', False) is False

    data['is_active'] = True
    response = await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': campaign_id},
        json=data,
        headers={'X-Yandex-Login': 'user'},
    )
    assert response.status == 200

    data = await response.json()
    assert data['campaign_type'] == 'regular'
    assert data['is_active'] is True

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(data['id'])
    assert campaign.is_active is True


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['regular_campaigns.sql'])
async def test_get_regular_campaign(web_context, web_app_client):
    campaign_id = 1001
    response = await web_app_client.get(
        '/v1/campaigns/item', params={'id': campaign_id},
    )
    assert response.status == 200

    response = await response.json()

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(response['id'])
    assert campaign.is_regular == (response['campaign_type'] == 'regular')
    assert campaign.regular_start_time == parse_datetime(
        response['regular_start_time'],
    )
    assert campaign.regular_stop_time == parse_datetime(
        response['regular_stop_time'],
    )


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.parametrize(
    'start_time, stop_time, result',
    [('2021-01-01T03:00:00+0000', '2021-02-01T03:00:00+0000', 201)],
)
async def test_create_campaign_w_efficiency_period(
        web_context,
        web_app_client,
        load_json,
        start_time,
        stop_time,
        result,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    data = load_json('campaign_new.json')['campaign_1']
    data['efficiency_start_time'] = start_time
    data['efficiency_stop_time'] = stop_time
    owner = 'user_owner'
    response = await web_app_client.post(
        '/v1/campaigns/item', json=data, headers={'X-Yandex-Login': owner},
    )
    assert response.status == result
    if result == 201:
        resp = await response.json()

        assert parse_datetime(resp['efficiency_start_time']) == parse_datetime(
            data['efficiency_start_time'],
        )
        assert parse_datetime(resp['efficiency_stop_time']) == parse_datetime(
            data['efficiency_stop_time'],
        )

        campaign_id = resp['id']
        db_campaign = storage.DbCampaign(web_context)
        campaign = await db_campaign.fetch(campaign_id)

        assert campaign.efficiency_start_time == parse_datetime(
            data['efficiency_start_time'],
        )
        assert campaign.efficiency_stop_time == parse_datetime(
            data['efficiency_stop_time'],
        )


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
async def test_campiagn_qs_version(
        web_context,
        web_app_client,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        load_json,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issue', 'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={'key': 'new_ticket_key'})

    params = load_json('campaign_new.json')['campaign_1']
    params['qs_schema_version'] = '10'

    owner = 'user'
    response = await web_app_client.post(
        '/v1/campaigns/item', json=params, headers={'X-Yandex-Login': owner},
    )
    assert response.status == 201

    params = await response.json()
    assert params['qs_schema_version'] == '10'

    params['qs_schema_version'] = '11'
    response = await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': params['id']},
        json=params,
        headers={'X-Yandex-Login': owner},
    )
    assert response.status == 200

    params = await response.json()
    assert params['qs_schema_version'] == '11'


@pytest.mark.config(CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2020-03-20 10:00:00')
@pytest.mark.parametrize(
    'update_id, trend, methods',
    [
        ('campaign_2', 'non_promo1', []),
        ('campaign_3', 'promo', ['motivation_1', 'motivation_2']),
        ('campaign_4', 'non_promo3', []),
    ],
)
async def test_update_campaign_with_motivation(
        web_context,
        web_app_client,
        load_json,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        update_id,
        trend,
        methods,
):
    updated_form = load_json('campaign_updated.json')[update_id]

    ticket = updated_form['ticket']
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']
    url = st_settings['robot-crm-admin']['url'] + f'issues/{ticket}/comments'

    @patch_aiohttp_session(url, 'POST')
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    response = await web_app_client.put(
        '/v1/campaigns/item',
        params={'id': 1},
        json=updated_form,
        headers={'X-Yandex-Login': 'user_owner'},
    )

    assert response.status == 200

    async with web_context.pg.master_pool.acquire() as conn:
        computed = await conn.fetchrow(
            'SELECT * FROM crm_admin.campaign WHERE id = 1',
        )

    assert computed['trend'] == trend
    assert computed['motivation_methods'] == methods
