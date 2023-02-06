# coding: utf-8

import pandas

from projects.common import wiki


class TestWiki:
    def test_from_dataframe(self):
        df = pandas.DataFrame.from_dict(
            {'num': [1.111, 2, 3], 'str': ['a', 'b', 'c'], 'int': [1, 2, 3]},
        )
        df.index = [2, 4, 6]

        formatted = wiki.from_dataframe(
            df, float_format='{:.1f}', use_header=True, use_index=True,
        )
        assert (
            formatted
            == '#|\n|| index | num | str | int ||\n|| 2 | 1.1 | a | 1 ||\n'
            '|| 4 | 2.0 | b | 2 ||\n|| 6 | 3.0 | c | 3 ||\n|#'
        )

        formatted = wiki.from_dataframe(
            df, float_format='{:.1f}', use_header=False, use_index=False,
        )
        assert (
            formatted == '#|\n|| 1.1 | a | 1 ||\n|| 2.0 | b | 2 ||\n'
            '|| 3.0 | c | 3 ||\n|#'
        )
