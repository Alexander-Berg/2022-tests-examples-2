from callcenter_etl.layer.yt.ods.oktell.common.impl import parse_phone_str, ParsedRow


def test_fixed_price_order_flg():
    assert parse_phone_str('79010010101') == ParsedRow(phone='+79010010101', city=None, brand=None, sip=None,
                                                       support_flg=False, inform_ivr_flg=False, cargo_flg=False,
                                                       other=None)
    assert parse_phone_str('89010010101') == ParsedRow(phone='+79010010101', city=None, brand=None, sip=None,
                                                       support_flg=False, inform_ivr_flg=False, cargo_flg=False,
                                                       other=None)
    assert parse_phone_str('9010010101') == ParsedRow(phone='+79010010101', city=None, brand=None, sip=None,
                                                      support_flg=False, inform_ivr_flg=False, cargo_flg=False,
                                                      other=None)

    assert parse_phone_str('79010010101&bla&bla-bla') == ParsedRow(phone='+79010010101', city=None, brand=None, sip=None,
                                                                   support_flg=False, inform_ivr_flg=False,
                                                                   cargo_flg=False, other=None)
    assert parse_phone_str('89010010101&bla&bla-bla') == ParsedRow(phone='+79010010101', city=None, brand=None, sip=None,
                                                                   support_flg=False, inform_ivr_flg=False,
                                                                   cargo_flg=False, other=None)
    assert parse_phone_str('9010010101&bla&bla-bla') == ParsedRow(phone='+79010010101', city=None, brand=None, sip=None,
                                                                  support_flg=False, inform_ivr_flg=False,
                                                                  cargo_flg=False, other=None)

    assert parse_phone_str('+79010010101') == ParsedRow(phone='+79010010101', city=None, brand=None, sip=None,
                                                        support_flg=False, inform_ivr_flg=False, cargo_flg=False,
                                                        other=None)
    assert parse_phone_str('+89010010101') == ParsedRow(phone='+89010010101', city=None, brand=None, sip=None,
                                                        support_flg=False, inform_ivr_flg=False, cargo_flg=False,
                                                        other=None)
    assert parse_phone_str('+9010010101') == ParsedRow(phone='+9010010101', city=None, brand=None, sip=None,
                                                       support_flg=False, inform_ivr_flg=False, cargo_flg=False,
                                                       other=None)

    assert parse_phone_str('79010010101-moscow') == ParsedRow(phone='+79010010101', city='moscow', brand='yandex',
                                                              sip=None, support_flg=False, inform_ivr_flg=False,
                                                              cargo_flg=False, other=None)
    assert parse_phone_str('89010010101-moscow') == ParsedRow(phone='+79010010101', city='moscow', brand='yandex',
                                                              sip=None, support_flg=False, inform_ivr_flg=False,
                                                              cargo_flg=False, other=None)
    assert parse_phone_str('9010010101-moscow') == ParsedRow(phone='+79010010101', city='moscow', brand='yandex',
                                                             sip=None, support_flg=False, inform_ivr_flg=False,
                                                             cargo_flg=False, other=None)

    assert parse_phone_str('74999999999-moscow-499') == ParsedRow(phone='+74999999999', city='moscow', brand='yandex',
                                                                  sip=None, support_flg=False, inform_ivr_flg=False,
                                                                  cargo_flg=False, other=None)

    assert parse_phone_str('79010010101-moscow-499') == ParsedRow(phone='+79010010101', city='moscow-499',
                                                                  brand='yandex', sip=None, support_flg=False,
                                                                  inform_ivr_flg=False, cargo_flg=False, other=None)
    assert parse_phone_str('89010010101-moscow-499') == ParsedRow(phone='+79010010101', city='moscow-499',
                                                                  brand='yandex', sip=None, support_flg=False,
                                                                  inform_ivr_flg=False, cargo_flg=False, other=None)
    assert parse_phone_str('9010010101-moscow-499') == ParsedRow(phone='+79010010101', city='moscow-499', brand='yandex',
                                                                 sip=None, support_flg=False, inform_ivr_flg=False,
                                                                 cargo_flg=False, other=None)

    assert parse_phone_str('79010010101-moscow--vezet') == ParsedRow(phone='+79010010101', city='moscow', brand='vezet',
                                                                     sip=None, support_flg=False, inform_ivr_flg=False,
                                                                     cargo_flg=False, other=None)
    assert parse_phone_str('89010010101-moscow--vezet') == ParsedRow(phone='+79010010101', city='moscow', brand='vezet',
                                                                     sip=None, support_flg=False, inform_ivr_flg=False,
                                                                     cargo_flg=False, other=None)
    assert parse_phone_str('9010010101-moscow--vezet') == ParsedRow(phone='+79010010101', city='moscow', brand='vezet',
                                                                    sip=None, support_flg=False, inform_ivr_flg=False,
                                                                    cargo_flg=False, other=None)

    assert parse_phone_str('79010010101-leninsk-kuzneckij') == ParsedRow(phone='+79010010101', city='leninsk-kuzneckij',
                                                                         brand='yandex', sip=None, support_flg=False,
                                                                         inform_ivr_flg=False, cargo_flg=False,
                                                                         other=None)
    assert parse_phone_str('89010010101-leninsk-kuzneckij') == ParsedRow(phone='+79010010101', city='leninsk-kuzneckij',
                                                                         brand='yandex', sip=None, support_flg=False,
                                                                         inform_ivr_flg=False, cargo_flg=False,
                                                                         other=None)
    assert parse_phone_str('9010010101-leninsk-kuzneckij') == ParsedRow(phone='+79010010101', city='leninsk-kuzneckij',
                                                                        brand='yandex', sip=None, support_flg=False,
                                                                        inform_ivr_flg=False, cargo_flg=False,
                                                                        other=None)

    assert parse_phone_str('79010010101-leninsk-kuzneckij--vezet') == ParsedRow(phone='+79010010101',
                                                                                city='leninsk-kuzneckij', brand='vezet',
                                                                                sip=None, support_flg=False,
                                                                                inform_ivr_flg=False, cargo_flg=False,
                                                                                other=None)
    assert parse_phone_str('89010010101-leninsk-kuzneckij--vezet') == ParsedRow(phone='+79010010101',
                                                                                city='leninsk-kuzneckij', brand='vezet',
                                                                                sip=None, support_flg=False,
                                                                                inform_ivr_flg=False, cargo_flg=False,
                                                                                other=None)
    assert parse_phone_str('9010010101-leninsk-kuzneckij--vezet') == ParsedRow(phone='+79010010101',
                                                                               city='leninsk-kuzneckij', brand='vezet',
                                                                               sip=None, support_flg=False,
                                                                               inform_ivr_flg=False, cargo_flg=False,
                                                                               other=None)

    assert parse_phone_str('79010010101-cargo-moscow--vezet') == ParsedRow(phone='+79010010101', city='moscow',
                                                                           brand='vezet', sip=None, support_flg=False,
                                                                           inform_ivr_flg=False, cargo_flg=True,
                                                                           other=None)
    assert parse_phone_str('89010010101-cargo-moscow--vezet') == ParsedRow(phone='+79010010101', city='moscow',
                                                                           brand='vezet', sip=None, support_flg=False,
                                                                           inform_ivr_flg=False, cargo_flg=True,
                                                                           other=None)
    assert parse_phone_str('9010010101-cargo-moscow--vezet') == ParsedRow(phone='+79010010101', city='moscow',
                                                                          brand='vezet', sip=None, support_flg=False,
                                                                          inform_ivr_flg=False, cargo_flg=True,
                                                                          other=None)

    assert parse_phone_str('79010010101-cargo-leninsk-kuzneckij--vezet') == ParsedRow(phone='+79010010101',
                                                                                      city='leninsk-kuzneckij',
                                                                                      brand='vezet', sip=None,
                                                                                      support_flg=False,
                                                                                      inform_ivr_flg=False,
                                                                                      cargo_flg=True, other=None)
    assert parse_phone_str('89010010101-cargo-leninsk-kuzneckij--vezet') == ParsedRow(phone='+79010010101',
                                                                                      city='leninsk-kuzneckij',
                                                                                      brand='vezet', sip=None,
                                                                                      support_flg=False,
                                                                                      inform_ivr_flg=False,
                                                                                      cargo_flg=True, other=None)
    assert parse_phone_str('9010010101-cargo-leninsk-kuzneckij--vezet') == ParsedRow(phone='+79010010101',
                                                                                     city='leninsk-kuzneckij',
                                                                                     brand='vezet', sip=None,
                                                                                     support_flg=False,
                                                                                     inform_ivr_flg=False,
                                                                                     cargo_flg=True, other=None)

    assert parse_phone_str('9955') == ParsedRow(phone=None, city=None, brand=None, sip=None, support_flg=True,
                                                inform_ivr_flg=False, cargo_flg=False, other=None)
    assert parse_phone_str('9955') == ParsedRow(phone=None, city=None, brand=None, sip=None, support_flg=True,
                                                inform_ivr_flg=False, cargo_flg=False, other=None)
    assert parse_phone_str('9955') == ParsedRow(phone=None, city=None, brand=None, sip=None, support_flg=True,
                                                inform_ivr_flg=False, cargo_flg=False, other=None)

    assert parse_phone_str('84951222453') == ParsedRow(phone=None, city=None, brand=None, sip=None, support_flg=False,
                                                       inform_ivr_flg=True, cargo_flg=False, other=None)
    assert parse_phone_str('84951222453') == ParsedRow(phone=None, city=None, brand=None, sip=None, support_flg=False,
                                                       inform_ivr_flg=True, cargo_flg=False, other=None)
    assert parse_phone_str('84951222453') == ParsedRow(phone=None, city=None, brand=None, sip=None, support_flg=False,
                                                       inform_ivr_flg=True, cargo_flg=False, other=None)

    assert parse_phone_str('is_disp') == ParsedRow(phone=None, city=None, brand=None, sip=None, support_flg=False,
                                                   inform_ivr_flg=False, cargo_flg=False, other='is_disp')

    assert parse_phone_str('sip:9944@37.228.115.27') == ParsedRow(phone=None, city=None, brand=None,
                                                                  sip='9944@37.228.115.27', support_flg=False,
                                                                  inform_ivr_flg=False, cargo_flg=False, other=None)
    assert parse_phone_str('sip:9944@37.228.115.27&blb-bla-cargo-moscow') == ParsedRow(phone=None, city=None,
                                                                                       brand=None,
                                                                                       sip='9944@37.228.115.27',
                                                                                       support_flg=False,
                                                                                       inform_ivr_flg=False,
                                                                                       cargo_flg=False, other=None)
