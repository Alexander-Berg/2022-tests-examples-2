import pytest


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'], dyn_table_data=['yt_events_data.yaml'],
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data.sql'])
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_corrupted_create(
        processing, yt_apply, pgsql,
):
    item_id = '14648896842964516938'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('aa1032d8398e4b8d9cf536ed8c8503bf', False, -5, -5, False),
        ('9d82dcbc629e48b7a904000c7a06fb00', False, -4, -4, False),
        ('10711b618f7e417c9d792632cb975dc8', False, -3, -3, False),
        ('f1dc3581e4e041b58532148462147e4e', False, -2, -2, False),
        ('d02d73484ebb4d9cadbe3aaebceb800e', False, -1, -1, False),
        ('961efda8b0ae413d8d646a1a8e451385', False, 0, 0, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_broken_idempotency.yaml'],
)
@pytest.mark.pgsql(
    'processing_db', files=['pg_events_data_broken_idempotency.sql'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_broken_idempotency(
        processing, yt_apply, pgsql,
):
    item_id = '17017711809348453172'
    await processing.testsuite.foo.call(item_id)
    # event 1d1ac550481a418a91eb6213b308c0bc deduped by idempotency_token
    assert _fetch_from_pg(pgsql, item_id) == [
        ('d089d12167374cc9881f5565278701b1', False, -4, -4, False),
        ('e9d7f9fe160441ef919153141e6cc4ea', False, -3, -3, False),
        ('1d1ac550481a418a91eb6213b308c0bc', False, -5, -2, True),
        ('c6faf3d4c1df45bc9ea75503f370f370', False, -1, -1, False),
        ('11e9c40cbfce4250887403f2e22efe99', False, 0, 0, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_broken_idempotency_no_pg.yaml'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_broken_idempotency_no_pg(
        processing, yt_apply, pgsql,
):
    item_id = '13725623758588348518'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('061d2e5d14554d05a1ae306c38ac6bc0', False, -12, 1, False),
        ('3c3ab65af19e4952a0392799c87d4736', False, -11, 2, False),
        ('bee4988505d7441fba991a579ea94cfa', False, -10, 3, False),
        ('a3ec1f0908f545a6a611799720e26a17', False, -9, 4, False),
        ('87191490c4b94b2e8710492aaca78121', False, -13, 5, True),
        ('36447e336e1348e9a6d8d2119a820a9b', False, -7, 6, False),
        ('6f87df536b79485fb46aac2fcbf94b87', False, -14, 7, True),
        ('c20a5de141aa46dd9ff50da70b1d5a74', False, -5, 8, False),
        ('109a8472c3c9454bbefae62988b3f568', False, -15, 9, True),
        ('e2eafa56669f47d793f7f7cb621e872a', False, -3, 10, False),
        ('88fb0493134d436cb5e009b77f2451d4', False, -16, 11, True),
        ('dd5e72fcf49d4bb095be6d63846273ff', False, -1, 12, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_many_copies_no_pg.yaml'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_many_copies_no_pg(
        processing, yt_apply, pgsql,
):
    item_id = '14819997a1e1123cbf95142219d93c17'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('7d4321ab1063441f975ca6f26d1322df', False, -73, 1, False),
        ('ed7f8792f371474baa59beecf52c600d', False, -71, 2, False),
        ('fa43a106476e4aa4b0229f51f1a9c883', False, -70, 3, False),
        ('da8036f45d9543919fc9c5cd0b8799e2', False, -69, 4, False),
        ('dafbdb2a3fd447008a1161bea490d1ac', False, -72, 5, False),
        ('2b9798cf4938458a87865dc51f5466a5', False, -68, 6, False),
        ('bb8d2e5aedce4babb4463f22a3cc15f2', False, -67, 7, False),
        ('49447f8dff2644bca74b12f9232d803a', False, -66, 8, False),
        ('1dbb76b8e6924cf99f22e303f7442be7', False, -65, 9, False),
        ('81a176c63878477b90524eb6f88709cc', False, -64, 10, False),
        ('0c4face3e80a4816a501d18c5809c8bf', False, -63, 11, False),
        ('11c73d71de98443e9a6d5e9497937d40', False, -74, 12, True),
        ('4a3d35ed875d4fea8ab58d29479d7f3d', False, -75, 13, True),
        ('1d71b108c74e4bfb9d22c6682d8b1066', False, -76, 14, True),
        ('3ca908ea1b1945ccb84cdd9758c39031', False, -77, 15, True),
        ('b12a6caae62a4e9fa9420a71444b5df1', False, -78, 16, True),
        ('0e47d1a33a4b4f9ea942565a0fb3cd9d', False, -79, 17, True),
        ('e7e3d08a22e347b98d00fb32e0611eeb', False, -80, 18, True),
        ('d4807dc53de3425085833384e1107871', False, -81, 19, True),
        ('94a4b29f11114c2a9883d171f1c2a344', False, -82, 20, True),
        ('5a1668466f0549459b4882df70fb1a52', False, -83, 21, True),
        ('7246f8f0d7e34a01b36defca646dc1cf', False, -52, 22, False),
        ('c824aa7c85f14e37bd43f9d54109748a', False, -51, 23, False),
        ('197aa0796bb44c959ba27afdf3c6e8d8', False, -50, 24, False),
        ('317bfa1ce7654499a8211a5e67412d73', False, -84, 25, True),
        ('58bd2735107c41c1a85fc27e85f6c5d7', False, -85, 26, True),
        ('b270cc65822643798edf5964382598d2', False, -86, 27, True),
        ('dc3cf2b747f647a382ddbb7193685d85', False, -87, 28, True),
        ('430d869f2ea34e4c8bc83d745c183c87', False, -88, 29, True),
        ('3214e3321b2b45c695dfa971464274c8', False, -89, 30, True),
        ('1ad8383b4a004f729a950224c58c4990', False, -90, 31, True),
        ('bf6cc1c0cba949278d430e30a2c9884b', False, -91, 32, True),
        ('5682da129ed64ddbb33327c320a51935', False, -92, 33, True),
        ('d14808526a094ce0b2993f998399fcc3', False, -93, 34, True),
        ('acef1a8c87bb423889c9d8f8f946b181', False, -94, 35, True),
        ('2c1944f1386b48c6a94668eea610a0e2', False, -95, 36, True),
        ('fa407ba58b30425cb6b6029a7d664f7a', False, -96, 37, True),
        ('b6f3368df2ac40d689873d43ccb540fd', False, -36, 38, False),
        ('76c9e9722e314058add7964a0c1ab643', False, -97, 39, True),
        ('b763f7ff61ff41738becc552f48c9438', False, -98, 40, True),
        ('97990f7087ba4cfaafb5cef8a2887fa5', False, -99, 41, True),
        ('92b423df78f04f87b15fa04891b4ac20', False, -100, 42, True),
        ('ec437a0d88594f1594f9bd4a76635135', False, -101, 43, True),
        ('ab4f524068a847dfa256e17e24adbb76', False, -102, 44, True),
        ('87877c1c536543639e875554cf57153c', False, -103, 45, True),
        ('07e38986d175441999de3c648ab753ec', False, -104, 46, True),
        ('376e350d7c1c4128acb1feb255e1342b', False, -105, 47, True),
        ('d991d2c0a0744d7da733fc9142d6d8a8', False, -106, 48, True),
        ('1dd328856d4a4480a970ad1d17822ca5', False, -107, 49, True),
        ('dec87cf739754517a8baa0aee41953c2', False, -108, 50, True),
        ('85331070b9fc47caa81d42b140842f7b', False, -109, 51, True),
        ('632858d925f34be8ac8d629bdbe5accf', False, -110, 52, True),
        ('ea578853044848a39ab31cf07791e249', False, -21, 53, False),
        ('da5bbf880e9d4cc4ac1285c1ff93aa05', False, -20, 54, False),
        ('98f8608b63c442d3bb54e0ae8372afeb', False, -19, 55, False),
        ('0fb06630a4ea4113b7885553981f06d2', False, -111, 56, True),
        ('24dd77abf0a84630961a9785d01a599d', False, -112, 57, True),
        ('7c6cba62eab9481ba2fb13f16b4f7722', False, -113, 58, True),
        ('47095d0336394a8ebf271e5813225d0b', False, -114, 59, True),
        ('6fd2f28cf81f4ae6a4f68230c1cc5d38', False, -115, 60, True),
        ('8dfebc845a554fb2ab78d46195b28a33', False, -116, 61, True),
        ('4fb940ba3075415cb061466ba69b32bc', False, -117, 62, True),
        ('bc919c737c5c457f95dbc6eab10934cf', False, -118, 63, True),
        ('f5d9d1b365ac466a96ac26744aacb6cf', False, -119, 64, True),
        ('ef3a15889c6c49048081d3155e37c3d6', False, -120, 65, True),
        ('e60456283293449eadf1c13c9a5179d4', False, -121, 66, True),
        ('af36d325b7a94e56a46c5058d5768751', False, -122, 67, True),
        ('82a054b4b76649c99b6140bcaac7f520', False, -123, 68, True),
        ('fa702129b41947c4ac47e8a539a22ffa', False, -124, 69, True),
        ('4cda78c8ae2342a9b589614aaeeea083', False, -125, 70, True),
        ('ab276060d0ad475c9291d950ce6657ac', False, -126, 71, True),
        ('cb99de7f40ed4f859156dd528732ec54', False, -127, 72, True),
        ('e64b6ce7ff054e6c9ebca7329b8a1e14', False, -1, 73, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_tight_creates.yaml'],
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data_tight_creates.sql'])
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_tight_creates(
        processing, yt_apply, pgsql,
):
    item_id = '14648896842964516938'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('10711b618f7e417c9d792632cb975dc8', False, -2, -2, False),
        ('961efda8b0ae413d8d646a1a8e451385', False, -1, -1, False),
        ('f80e6c8358bbd68ea62c058ec97ddfe3', False, 0, 0, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_handled.yaml'],
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data_handled.sql'])
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_handled(processing, yt_apply, pgsql):
    item_id = '14648896842964516938'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('10711b618f7e417c9d792632cb975dc8', False, -2, -2, False),
        ('961efda8b0ae413d8d646a1a8e451385', False, -1, -1, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_handled_reversed.yaml'],
)
@pytest.mark.pgsql(
    'processing_db', files=['pg_events_data_handled_reversed.sql'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_handled_reversed(
        processing, yt_apply, pgsql,
):
    item_id = '14648896842964516938'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('961efda8b0ae413d8d646a1a8e451385', False, -1, -2, False),
        ('10711b618f7e417c9d792632cb975dc8', False, -2, -1, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_keep.yaml'],
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data_keep.sql'])
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_keep(processing, yt_apply, pgsql):
    item_id = '14648896842964516938'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('10711b618f7e417c9d792632cb975dc8', False, -1, -1, False),
        ('961efda8b0ae413d8d646a1a8e451385', True, 0, 0, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_single.yaml'],
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data_single.sql'])
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_single(processing, yt_apply, pgsql):
    item_id = '14648896842964516938'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('961efda8b0ae413d8d646a1a8e451385', True, 0, 0, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_merge_same.yaml'],
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data_merge_same.sql'])
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_merge_same(processing, yt_apply, pgsql):
    item_id = '14648896842964516938'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('849c0c8e1b8d2029fc1b72119c9af5b5', False, -1, -1, False),
        ('961efda8b0ae413d8d646a1a8e451385', True, 0, 0, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_merge_new.yaml'],
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data_merge_new.sql'])
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_merge_new(processing, yt_apply, pgsql):
    item_id = '14648896842964516938'
    await processing.testsuite.foo.call(item_id)
    assert _fetch_from_pg(pgsql, item_id) == [
        ('849c0c8e1b8d2029fc1b72119c9af5b5', False, -2, -2, False),
        ('961efda8b0ae413d8d646a1a8e451385', False, -1, -1, False),
        ('f4b0d39d16566fcc559a1f5bbc16ce56', True, 0, 0, False),
    ]


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_data_for_another_ugly_case.yaml'],
)
@pytest.mark.pgsql(
    'processing_db', files=['pg_events_for_another_ugly_case.sql'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
async def test_procaas_restore_dedup_another_ugly_case(
        processing, yt_apply, pgsql,
):
    item_id = 'a6a79bab978f4af2a82723dce86253cd'
    await processing.testsuite.foo.call(item_id)
    from_pg = _fetch_from_pg(pgsql, item_id)
    assert [i for i in from_pg if not i[4]] == [
        ('51d698edc28a492e8717fa9ed66fe53f', False, -70, -70, False),
        ('705cea509bb94a57bcd87b3d124ce071', False, -69, -69, False),
        ('77dadbafa2704683b883a107c9b3a435', False, -68, -68, False),
        ('1ef5210264b447b3b74e7928eb56ea6e', False, -8, -8, False),
    ]
    assert {i[0] for i in from_pg if i[4]} == {
        'cfc93719d2dc49b69c621bb53b14e94b',
        '0c789edc829d4923828cbb14e7c4299c',
        '52f6466154324514995996146a520d7d',
        'f02d823c1f77489ebbe52ab1ee451718',
        '3f02e58e84274d05a77d834a8ec80887',
        '4430ba99f57f43db8a84f10e5ae201a6',
        'b79d9f08379f4545b33fcaccfe15b2d5',
        '34abf84f265248bc833f0ca8cfeaa376',
        '5f8926e2ca244c62ac758b55f4d135b7',
        'dfb7cddcf5204a5f8be511ec01e42acb',
        '26c25e350819415299893f04cbe608f0',
        'cdd00b37174143288b71de468f35477d',
        'cbb1967351414f549df575372b9b4857',
        'f1b630d0f33440caaa323379f13ad17a',
        '7fce8ebf818b4ba28a2949e97839f9bc',
        'ed24124212664e15b1cd677f8aac555b',
        'cd0a4dfcc809455bb0456cbc0afe2052',
        '114bc1b4151c46fda09eefb657594a3a',
        '265fe22ed0ac49c589c8106dc2524f2d',
        'f6e723ec0e434ccabaeb3c50c6a72256',
        'a9af64f051394285b108b794d29c23ea',
        '6e37272cf31f4eefa226987615bf898a',
        '66e109669d554a8c99ffd0bf4fc9915a',
        'f0167b81dfdc47959dc5d3551cb861aa',
        '5b030aa91fc4442b902449e7890223f1',
        '1ac94d58a11c4004a5a37ba64928ce2a',
        '3cea01d4a75b4665825e213b4239af93',
        '0ea792a2924c436a8dc75a7dcdd7b391',
        '0b13955765134f968f49802ef3c07fb3',
        'c3813f58509e4970924aa0ca9d4008df',
        '4317bb6265f04c7e98a26eaff5749747',
        'eb0c34c6ab0648d8a5ccfe3bdeea4942',
        '2ce2216e7e3047cebdc4474d689324f9',
        'ff9c55fefb2541cfb0ed96807bddbf64',
        '501b6d0519f443b2ab359c0a5ecfc508',
        '292d768f52e24825b1e20cf3937a9ae2',
        'cc16501c171445499623db406462ca86',
        'ef5b3dd4b1894a2daf3dda6cd6cbdd43',
        '66bb202d936145349962f5a701a1e1af',
        'c9792723e12e427ea0fa8d29b95822ab',
        'c0316aef92f44cccb964a2247f6dfa55',
        '003c1099122848efa6cfacf9b9fd86a4',
        '6bf9b82de5bb4c6fa7819587e8fe9d0e',
        '1df975ff976744b9a9f044bd9b7841fd',
        '0fb07735c6ee4e1ea63de886d0dd4776',
        '002cd0eef0bc46868a268e381aa485b6',
        '64bce1253f5e420eb7f096020233ede3',
        '150ca14eb7f04db1886e9529d22964e3',
        'f12e0450a18f42b99452b1e81bf82f86',
        'efda2283cb4e4b8087e08fa45c83b2e9',
        '1287ad01ad6b4e25aea189d345f9ff71',
        '2f7de2a286b34989b30f473e95cbe0b4',
        'ca9d57b9081c46c5b0ff403a7041cde3',
        '22176641b6d843cbbf1972c978e56ed8',
        'f8f5174e06cb408995e94bf9aeda3740',
        'bd0128913c284f588a79ac62edfd842e',
        '740c1bceddff4680a54d8a0f09325fcf',
        '4bc2a3853d834d1384ce1da719f081f8',
        'e4ca968ef3294ea8821fcce09e57969c',
        'c35b3101419b46dba6a4c9644b46f4ac',
        'd9d6492a544b432d81774f7f4001901b',
        'f32eee99a71e422998b50a1b5cdfc70b',
        'a5e84e5592d84de4b8dda5c3ba72e18d',
        'a03e062a122445f48f8e7848c8d03ab4',
        'e8b803ad90a24f74b173b9a8ba08fd8b',
        'ba1fe87a8f014698b16082a25796b8b1',
    }


def _fetch_from_pg(pgsql, item_id):
    cursor = pgsql['processing_db'].cursor()
    cursor.execute(
        'SELECT event_id, need_handle, order_key, handling_order_key, '
        'is_duplicate '
        'FROM processing.events '
        'WHERE item_id=%(item_id)s ORDER BY handling_order_key, order_key',
        {'item_id': item_id},
    )
    return list(cursor)
