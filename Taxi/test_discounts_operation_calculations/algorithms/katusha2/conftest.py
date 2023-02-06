import io


import pandas as pd
import pytest


@pytest.fixture(scope='function')
def create_dataframe():
    def make(raw_data: str):
        processed = '\n'.join(map(str.strip, raw_data.split('\n')))
        data_frame = pd.read_csv(io.StringIO(processed), sep=',')
        data_frame = data_frame.set_index(
            ['segment', 'price_from', 'discount'],
        )
        return data_frame

    return make
