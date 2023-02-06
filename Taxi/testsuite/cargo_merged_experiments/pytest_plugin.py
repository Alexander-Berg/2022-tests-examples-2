import pytest


def _get_merge_tag(consumers):
    return [
        {
            'consumer': consumer,
            'merge_method': 'dicts_recursive_merge',
            'tag': 'cargo_extended_lookup',
        }
        for consumer in consumers
    ]


@pytest.fixture(name='exp_extended_tariffs')
def _exp_extended_tariffs(experiments3):
    async def _wrapper(
            client,
            *,
            consumers,
            enabled=True,
            delayed_classes=None,
            merge_tag='common',
            extra_delayed_classes=None,
            extra_classes=None,
    ):
        if delayed_classes is None:
            delayed_classes = ['courier']
        if extra_classes is None:
            # used in cargo-matcher only
            extra_classes = ['express']

        extended_tariffs_exp = {
            merge_tag: {
                'extended_tariffs': {
                    'extra_classes': extra_classes,
                    'delayed_classes': [
                        {
                            'taxi_classes': delayed_classes,
                            'delay': {'since_lookup': 900, 'since_due': -900},
                        },
                    ],
                },
            },
        }
        extended_tariffs = extended_tariffs_exp[merge_tag]['extended_tariffs']
        if extra_delayed_classes is not None:
            extended_tariffs['delayed_classes'].extend(extra_delayed_classes)

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': enabled},
            name=f'cargo_extended_tariffs_{merge_tag}',
            consumers=consumers,
            clauses=[],
            default_value=extended_tariffs_exp,
            merge_values_by=_get_merge_tag(consumers),
        )
        await client.invalidate_caches()

    return _wrapper
