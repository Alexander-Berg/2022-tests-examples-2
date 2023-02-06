import pytest

from blockstat import parse_blocks, BlocksValidationError, Block


class TestParseBlocks:
    def test_validates_string_is_not_empty(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('')
        assert e.value[0] == '"Blocks" field is empty'

    def test_validates_string_ends_with_tab(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('/test\t0\tstrange ending')
        assert e.value[0] == '"Blocks" field should end with tab, but it ends with "g"'

    def test_validates_vars_count_exists(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('/test\t')
        assert e.value[0] == 'Expected number of vars but got end of data'

    def test_validates_vars_count_format(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('/test\tabc\t')
        assert e.value[0] == "Could not parse number of vars from abc: invalid literal for int() with base 10: 'abc'"

    def test_validates_vars_count_value(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('/test\t-17\t')
        assert e.value[0] == 'Number of vars should 0 or more, but it is -17'

    def test_allows_vars_count_0(self):
        assert parse_blocks('/test\t0\t') == [Block('/test', {})]

    def test_validates_vars_count_is_not_more(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('/test\t2\ta=b\t')
        assert e.value[0] == 'Expected var but got end of data'

    def test_validates_var_equal_sign(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('/test\t1\tstrangevar\t')
        assert e.value[0] == 'Var strangevar does not match var pattern'

    def test_validates_var_key_length(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('/test\t1\t=15\t')
        assert e.value[0] == 'Var =15 does not match var pattern'

    def test_validates_var_value_length(self):
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks('/test\t1\tkey=\t')
        assert e.value[0] == 'Var key= does not match var pattern'

    def test_accepts_equal_sign_in_var_value(self):
        assert parse_blocks('/test\t1\tkey=wiz=test\t') == [Block('/test', {'key': 'wiz=test'})]

    def test_accepts_double_equal_sign_in_vars(self):
        assert parse_blocks('/test\t1\tkey==tt\t') == [Block('/test', {'key': '=tt'})]

    def test_several_vars(self):
        assert parse_blocks('/a\t3\tx=y\tsome=var\tother=value\t') == [
            Block('/a', {'x': 'y', 'some': 'var', 'other': 'value'})]

    def test_several_blocks(self):
        assert parse_blocks('/a\t0\t/b\t1\tx=y\t') == [Block('/a', {}), Block('/b', {'x': 'y'})]

    def test_real_fail_example(self):
        blocks = (
            '/\t0\t/head/logo\t0\t/header/clear\t0\t/header/microphone/start\t0\t/header/microphone/init\t0\t/header/mi'
            'crophone/stop\t0\t/header/microphone/first\t0\t/header/microphone/data\t0\t/header/microphone/error\t0\t/h'
            'eader/microphone/hide\t0\t/header/microphone\t0\t/serp/navig/www\t0\t/serp/navig/images\t0\t/serp/navig/vi'
            'deo\t0\t/serp/navig/maps\t0\t/serp/navig/market\t0\t/serp/navig/news\t0\t/serp/navig/translate\t0\t/serp/n'
            'avig/disk\t0\t/serp/navig/music\t0\t/serp/navig/mail\t0\t/serp/navig/all\t0\t/serp/navig/more\t0\t/region'
            '\t1\tid=213\t/test-ids\t1\tvalue=58545,60321,45969,60461,9346\t/tech/userlocation/on\t0\t/tech/userlocatio'
            'n/off\t0\t/tech/userlocation/granted\t0\t/tech/userlocation/denied\t0\t/tech/userlocation/prompt\t0\t/tech'
            '/userlocation/new\t0\t/tech/userlocation/old\t0\t/tech/userlocation/unknown\t0\t/search_props\t1\tstaticVe'
            '1513011363\tfuid01=5a2d98275cfce49e.Gc4Ct0yJJapaGfcOU0U96_lH7TpIWx3t_BRz4DlTO5n94gm7FKAGq9-kCZjy9AUxbPZzW4'
            'VFTuszqhzyYUeniezB_1e5DVokg8b7KuNByos3UJgbN0gjouMOugbo4n_2; _ym_uid=1512937494885276626; my=YwA=; yandexui'
            'd=1583820191512937491; _ym_isad=2; mda=0; yandex_gid=35; ys=wprid.1513005543766070-99305622190148931659731'
            '2-sas1-7458-TCH; yp=1528779180.szm.2_00:375x667:375x628#1528705512.sz.667x375x2#1515597546.shlos.0#1544502'
            '202.st_search_cl.1#1513139411.gpauto.45_062764:38_950778:1414:1:1512966611#1515565483.ygu.1; yc=1513270376'
            '.lp.1038%3A1033%2C1040%3A1423%2C1385%3A22#1513270560.ls.2136%3A141#1513250382.lr.76%3A2580%2C1038%3A2480%2'
            'C1040%3A543; i=JUuDmFPRA91OERfMU2+4nLaA3COHzFnBT19P2mmSyCGigG2K1IR5VKCUiYK9+MhlbcePzzdStXc4feh90LNBqxaItjM'
            '=\t95.153.130.19\t\t\thttps://www.yandex.ru/\tMozilla/5.0 (iPhone; CPU iPhone OS 9_3_1 like Mac OS X) Appl'
            'eWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13E238 Safari/601.1\tGET\t/search/touch/?text=%D0%'
            'BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4+%D1%81+%D0%BA%D0%B0%D1%80%D1%82%D1%8B+%D1%81%D0%B1%D0%B5%D1%80%D0%B'
            '1%D0%B0%D0%BD%D0%BA%D0%B0+%D0%BD%D0%B0+%D0%BA%D0%B0%D1%80%D1%82%D1%83+%D0%B0%D0%BB%D1%8C%D1%84%D0%B0+%D0%B'
            '1%D0%B0%D0%BD%D0%BA%D0%B0+%D0%BA%D0%BE%D0%BC%D0%B8%D1%81%D1%81%D0%B8%D1%8F&msid=1513011173.77.22891.15424&'
            'lr=35&mda=0&suggest_reqid=158382019151293749113624621130299\twww.yandex.ru\t1513011363033201-1154127732887'
            '135884209200-sas1-1990-TCH\t1583820191512937491\t'
        )
        with pytest.raises(BlocksValidationError) as e:
            parse_blocks(blocks)
        assert e.value[0] == 'Var staticVe1513011363 does not match var pattern'

    def test_real_example(self):
        blocks = (
            '/\t0\t/tr/images/index\t0\t/image/new/head/logo\t0\t/head/login/login\t0\t/head/login/register\t0\t/head/l'
            'ogin/popup/login\t0\t/head/login/popup/switch\t0\t/head/login/popup/close\t0\t/head/login/popup/promo/clos'
            'e\t0\t/head/login/popup/promo/show\t0\t/image/new/navig/search\t0\t/image/new/navig/images\t0\t/image/new/'
            'navig/video\t0\t/image/new/navig/maps\t0\t/image/new/navig/translate\t0\t/image/new/navig/disk\t0\t/image/'
            'new/navig/mail\t0\t/image/new/navig/all\t0\t/image/new/navig/more\t0\t/image/touch/preview/panel/share/can'
            'cel\t0\t/image/new/footer/feedback\t0\t/image/new/footer/help\t0\t/image/new/footer/license\t0\t/tr/images'
            '/index/ajax\t0\t/image/new/serp/submit/abuse\t0\t/tech/new/test\t2\t-nodereport=1\t-responseid=da39a3ee5e6'
            'b4b0d3255bfef95601890afd80709-65773-1512947241035-1979\t'
        )
        expected = [
            Block('/', {}),
            Block('/tr/images/index', {}),
            Block('/image/new/head/logo', {}),
            Block('/head/login/login', {}),
            Block('/head/login/register', {}),
            Block('/head/login/popup/login', {}),
            Block('/head/login/popup/switch', {}),
            Block('/head/login/popup/close', {}),
            Block('/head/login/popup/promo/close', {}),
            Block('/head/login/popup/promo/show', {}),
            Block('/image/new/navig/search', {}),
            Block('/image/new/navig/images', {}),
            Block('/image/new/navig/video', {}),
            Block('/image/new/navig/maps', {}),
            Block('/image/new/navig/translate', {}),
            Block('/image/new/navig/disk', {}),
            Block('/image/new/navig/mail', {}),
            Block('/image/new/navig/all', {}),
            Block('/image/new/navig/more', {}),
            Block('/image/touch/preview/panel/share/cancel', {}),
            Block('/image/new/footer/feedback', {}),
            Block('/image/new/footer/help', {}),
            Block('/image/new/footer/license', {}),
            Block('/tr/images/index/ajax', {}),
            Block('/image/new/serp/submit/abuse', {}),
            Block('/tech/new/test', {'-nodereport': '1', '-responseid': 'da39a3ee5e6b4b0d3255bfef95601890afd80709-65773-1512947241035-1979'}),
        ]
        assert parse_blocks(blocks) == expected
