import pytest

from pandas import DataFrame
from dmp_suite.personal.pandas_transform import add_fake_personal_data
from test_dmp_suite.utils import random_seed


@pytest.mark.slow
@pytest.mark.skip(reason='Тест флапает из-за проблем с TVM, которые пока не удалось разрешить. При запуске одиночного теста флап не воспроизводится.')
def test_fake_phones():
    # Чтобы случайные данные в тесте всегда были одинаковы:

    with random_seed(1):
        df = DataFrame([{'name': 'Sasha'}, {'name': 'Masha'}])
        new_df = add_fake_personal_data(df, 'phone', 'phone_id')

        # Cтарый dataframe должен остаться без изменений:
        assert list(df) == ['name']

        # А в новом должны появиться две колонки:
        assert list(new_df) == ['name', 'phone', 'phone_id']

        assert new_df.iloc[0]['phone'] == '+79116411543'
        assert new_df.iloc[0]['phone_id'] == '5e4ab872cfe7484f81a79e1f49ed3dcf'

        assert new_df.iloc[1]['phone'] == '+79217521611'
        assert new_df.iloc[1]['phone_id'] == 'c2e5a9ab981642158dcd408e3200ec25'

