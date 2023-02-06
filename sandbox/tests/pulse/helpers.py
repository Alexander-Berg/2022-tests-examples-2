# coding=utf-8
from sandbox.projects.sandbox_ci import pulse


class TestPulseHelpersTest(object):
    def test_normalize_query(self):
        assert pulse.normalize_query('A  B  C  ') == 'a b c'
        assert pulse.normalize_query('A%"B*&/C') == 'a b c'
        assert pulse.normalize_query('$20 to RUR') == '$20 to rur'

        assert pulse.normalize_query('Порно') == 'порно'
        assert pulse.normalize_query(u'Порно') == 'порно'

    def test_get_text_from_url(self):
        url_path = (
            u'/search/pad/?lr=213&msid=1519482494.04292.22872.23871&text'
            u'=%D1%84%D0%BE%D1%80%D0%BC%D0%B0+%D0%B4%D0%BB%D1%8F+%D0%B2%D1%8B%D0%BF%D0'
            u'%B5%D1%87%D0%BA%D0%B8+%D1%82%D0%B5%D1%81%D0%BA%D0%BE%D0%BC%D0%B0+'
            u'&suggest_reqid=450894680151743919624973186151179'
        )
        assert pulse.get_text_from_url(url_path) == 'форма для выпечки тескома'
