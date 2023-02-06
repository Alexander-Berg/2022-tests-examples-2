import pytest

from sticker import db


@pytest.mark.parametrize(
    'columns_num, rows_num, should_fail, expected',
    [
        (
            1,
            5,
            False,
            '($1::text),($2::text),($3::text),($4::text),($5::text)',
        ),
        (2, 2, False, '($1::text,$2::text),($3::text,$4::text)'),
        (2 ** 8, 2 ** 8, True, ValueError),
    ],
)
def test_generate_prepare_expression(
        columns_num, rows_num, should_fail, expected,
):
    prepare_kwargs = {
        'column_types': ['text'] * columns_num,
        'rows_num': rows_num,
    }

    try:
        prepare_expression = db.generate_prepare_expression(**prepare_kwargs)
        if should_fail:
            assert False

        assert prepare_expression == expected
        return

    # pylint: disable=broad-except
    except Exception as err:
        assert should_fail and isinstance(err, expected)
