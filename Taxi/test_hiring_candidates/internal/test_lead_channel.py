# pylint: disable=no-member
import typing

import pydantic

from hiring_candidates.internal import eda_lead_channel


def test_get_condition_results(load_json):
    # arrange
    request = eda_lead_channel.LeadData(
        campaign='abc',
        lead_source_code='bca',
        utm_source='cab',
        retention=False,
    )
    conditions = pydantic.parse_obj_as(
        typing.Dict[str, eda_lead_channel.LeadChannelCondition],
        load_json('conditions.json'),
    )

    # act
    results = eda_lead_channel.get_conditions_results(request, conditions)

    # assert
    assert results == load_json('conditions_results.json')


def test_get_condition_results_nones(load_json):
    # arrange
    request = eda_lead_channel.LeadData(
        campaign=None, lead_source_code=None, utm_source=None, retention=False,
    )
    conditions = pydantic.parse_obj_as(
        typing.Dict[str, eda_lead_channel.LeadChannelCondition],
        load_json('conditions.json'),
    )

    # act
    results = eda_lead_channel.get_conditions_results(request, conditions)

    # assert
    assert set(results.values()) == {False}
