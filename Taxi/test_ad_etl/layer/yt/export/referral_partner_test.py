from ad_etl.layer.yt.export.referral_partner.agg_referral_partner_statistics_snp.loader import (
    extract_clid, extract_vid
)


def test_extract_clid_vid():
    for source_id, expected_identifiers in (
        ('1234567', {'clid': '1234567', 'vid': None}),
        ('1234567_dsada', {'clid': '1234567', 'vid': None}),
        ('1234567_1234', {'clid': '1234567', 'vid': None}),
        ('1234567_123', {'clid': '1234567', 'vid': '123'}),
        ('1234567_000', {'clid': '1234567', 'vid': None}),
        ('1234567_001', {'clid': '1234567', 'vid': '1'}),
        ('1234567_45', {'clid': '1234567', 'vid': '45'}),
        ('1234567_1', {'clid': '1234567', 'vid': '1'})
    ):
        for identifier_type, extractor in (
            ('clid', extract_clid),
            ('vid', extract_vid)
        ):
            actual_identifier = extractor(source_id)
            assert expected_identifiers[identifier_type] == actual_identifier, \
                'Expected {} for source id {} is different from actual:\nexpected {},\nactual {}' \
                    .format(identifier_type, source_id, expected_identifiers[identifier_type], actual_identifier)
