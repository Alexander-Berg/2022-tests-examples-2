from unittest import mock

import pytest

from taxi_antifraud.qc import yavtocod


@pytest.mark.parametrize(
    'yavtocod_name,qc_pass_name,matching,should_match',
    [
        (
            'МЕРСЕДЕС-БЕНЦ E 200 4MATIC Е СLАSS',
            'Mercedes-Benz',
            [{'qc_pass_name': 'Mercedes-Benz', 'yavtocod_name': 'МЕРСЕДЕС'}],
            True,
        ),
        (
            'ЛАДА 219070 ЛАДА ГРАНТА',
            'LADA (ВАЗ)',
            [{'qc_pass_name': 'LADA (ВАЗ)', 'yavtocod_name': 'ЛАДА'}],
            True,
        ),
        (
            'ЛАДА 219070 ЛАДА ГРАНТА',
            'Mercedes-Benz',
            [
                {'qc_pass_name': 'Mercedes-Benz', 'yavtocod_name': 'МЕРСЕДЕС'},
                {'qc_pass_name': 'LADA (ВАЗ)', 'yavtocod_name': 'ЛАДА'},
            ],
            False,
        ),
    ],
)
def test_brand_matching(yavtocod_name, qc_pass_name, matching, should_match):
    config = mock.Mock(
        AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_BRAND_MAPPING=matching,
    )

    assert (
        yavtocod.brands_are_matched(yavtocod_name, qc_pass_name, config)
        == should_match
    )
