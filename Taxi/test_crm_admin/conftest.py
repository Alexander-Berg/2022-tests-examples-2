# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import typing

import pytest

import crm_admin.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['crm_admin.generated.service.pytest_plugins']


@pytest.fixture(scope='function')
def campaign_exists(pgsql):
    def campaign_exists(campaign_id):
        cursor = pgsql['crm_admin'].cursor()
        query = 'SELECT * FROM crm_admin.trigger_campaign WHERE id = %s'
        cursor.execute(query, (campaign_id,))
        return cursor.fetchone() is not None

    return campaign_exists


@pytest.fixture(scope='function')
def get_campaign(pgsql):
    def get_campaign(campaign_id):
        cursor = pgsql['crm_admin'].cursor()
        query = 'SELECT * FROM crm_admin.trigger_campaign WHERE id = %s'
        cursor.execute(query, (campaign_id,))
        row = cursor.fetchone()
        columns = (item[0] for item in cursor.description)
        return dict(zip(columns, row))

    return get_campaign


@pytest.fixture(scope='function')
def is_campaign_exist(pgsql):
    def _is_campaign_exist(
            campaign_id,
            expected_campaign: typing.Optional[dict] = None,
            owner: typing.Optional[str] = None,
    ):

        cursor = pgsql['crm_admin'].cursor()
        query = f"""
            SELECT name, entity_type, owner_name
            FROM crm_admin.campaign
            WHERE id = {campaign_id};
        """
        cursor.execute(query)
        record = cursor.fetchone()
        if not record:
            return False
        if not expected_campaign:
            return True
        if (
                record[0] != expected_campaign['name']
                or record[1] != expected_campaign['entity']
        ):
            return False
        if owner is not None:
            if record[2] != owner:
                return False
        return True

    return _is_campaign_exist


@pytest.fixture(scope='function')
def is_filters_exist(pgsql):
    def _is_filters_exist(campaign_id, expected_settings):

        cursor = pgsql['crm_admin'].cursor()
        query = f"""
            SELECT settings
            FROM crm_admin.campaign
            WHERE id = {campaign_id};
        """
        cursor.execute(query)
        record = cursor.fetchone()

        if not record:
            return False

        retrieved_settings = record[0]

        return expected_settings == retrieved_settings

    return _is_filters_exist


@pytest.fixture(scope='function')
def check_campaign_state(pgsql):
    def _check_campaign_state(campaign_id, expected_state):
        cursor = pgsql['crm_admin'].cursor()
        query = f"""
            SELECT state
            FROM crm_admin.campaign
            WHERE id = {campaign_id};
        """
        cursor.execute(query)
        record = cursor.fetchone()
        retrieved_state = record[0]

        return expected_state == retrieved_state

    return _check_campaign_state


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'YQL_TOKEN': 'common_yql_token',
            'NIRVANA_OAUTH': 'nirvana_oauth_token',
            'STARTRACK_API_PROFILES': {
                'robot-crm-admin': {
                    'url': 'https://st-api.test.yandex-team.ru/v2/',
                    'org_id': 0,
                    'oauth_token': '',
                },
            },
            'S3MDS_TAXI_CRM_ADMIN': {
                'url': '',
                'bucket': '',
                'access_key_id': '',
                'secret_key': '',
            },
        },
    )
    return simple_secdist
