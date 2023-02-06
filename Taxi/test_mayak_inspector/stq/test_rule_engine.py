import pytest

from metrics_processing.rules import common as rules_common
from metrics_processing.rules.common import utils
from taxi.util import dates

from mayak_inspector.common.models import contractor
from mayak_inspector.common.models import metrics_event


@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'name': 'unique',
                'zone': 'default',
                'tariff': 'econom',
                'actions': [
                    {
                        'action': [
                            {
                                'tags': [
                                    {'name': 'ManyOTsWarning', 'ttl': 86400},
                                ],
                                'type': 'tagging',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'batching_check'}],
            },
        ],
    },
)
@pytest.mark.config(
    DRIVER_METRICS_TARIFF_TOPOLOGIES={
        '__default__': {'__default__': {'__default__': ['econom']}},
    },
)
def test_rule_engine(stq3_context):
    entity = contractor.Contractor(
        'mock_entity',
        mayak_entity_uuid=1,
        mayak_import_uuid=1,
        park_driver_profile_ids=dict(),
        driver_profiles=dict(),
    )
    entity.update_event(
        metrics_event.MetricsEvent(
            name='32',
            event_id='333',
            event_type='batching_check',
            timestamp=dates.utcnow(),
            entity_id='mock_entity',
            zone='helsinki',
        ),
    )
    tariff = 'econom'
    zone_chain = ['helsinki', 'default']

    tariff_config = utils.get_tariff_config(
        config=stq3_context.config.DRIVER_METRICS_TARIFF_TOPOLOGIES,
        tariff=tariff,
        zone_chain=zone_chain,
        default_zone=rules_common.CACHE_DEFAULT_ZONE,
    )

    actions = stq3_context.metrics_rules_config.apply(
        rule_type=rules_common.RuleType.DEFAULT,
        entity=entity,
        now=dates.utcnow(),
        use_config_service=True,
        tariff=tariff,
        tariff_config=tariff_config,
    )

    assert actions == [
        {
            'protected': False,
            'rule_config_id': None,
            'rule_name': 'unique',
            'tags': [{'name': 'ManyOTsWarning', 'ttl': 86400}],
            'triggered_context': {'tags': []},
            'type': 'tagging',
        },
    ]
