from collections import namedtuple


SocdemProfile = namedtuple('SocdemProfile', [
    'crypta_id',
    'age_segment_0_17_prb',
    'age_segment_18_24_prb',
    'age_segment_25_34_prb',
    'age_segment_35_44_prb',
    'age_segment_45_54_prb',
    'age_segment_55_99_prb',
    'gender_female_prb',
    'gender_male_prb',
    'has_children_0_1_years_flg',
    'has_children_11_16_years_flg',
    'has_children_1_3_years_flg',
    'has_children_3_6_years_flg',
    'has_children_6_11_years_flg',
    'has_children_wo_age_flg',
    'income_segment_a_prb',
    'income_segment_b1_prb',
    'income_segment_b2_prb',
    'income_segment_c1_prb',
    'income_segment_c2_prb',
    'predict_socdem_age_segment_code',
    'predict_socdem_gender_code',
    'predict_socdem_income_code',
])

InitReducerInput = namedtuple(
    'InitReducerInput',
    SocdemProfile._fields + ('effective_dt',)
)

AppendReducerInput = namedtuple(
    'AppendReducerInput',
    SocdemProfile._fields + ('effective_dt', 'order_col',)
)

DEFAULT_SOCDEM_PARAMS = dict(
    crypta_id='id1',
    age_segment_18_24_prb=0.0,
    age_segment_25_34_prb=0.0,
    age_segment_35_44_prb=0.0,
    age_segment_45_54_prb=0.0,
    age_segment_55_99_prb=0.0,
    gender_female_prb=0.0,
    gender_male_prb=0.0,
    has_children_0_1_years_flg=False,
    has_children_11_16_years_flg=False,
    has_children_1_3_years_flg=False,
    has_children_3_6_years_flg=False,
    has_children_6_11_years_flg=False,
    income_segment_a_prb=0.0,
    income_segment_b1_prb=0.0,
    income_segment_b2_prb=0.0,
    income_segment_c1_prb=0.0,
    income_segment_c2_prb=0.0,
    predict_socdem_age_segment_code='25_34',
    predict_socdem_gender_code='m',
)


def _build_init_input_record(effective_dt, age_prb=0.0, income_code='C1', children_flg=False):
    return InitReducerInput(
            effective_dt=effective_dt,
            age_segment_0_17_prb=age_prb,
            predict_socdem_income_code=income_code,
            has_children_wo_age_flg=children_flg,
            **DEFAULT_SOCDEM_PARAMS,
        )


def _build_append_input_record(effective_dt, age_prb=0.0, income_code='C1', children_flg=False, order_col=1):
    return AppendReducerInput(
            effective_dt=effective_dt,
            age_segment_0_17_prb=age_prb,
            predict_socdem_income_code=income_code,
            has_children_wo_age_flg=children_flg,
            order_col=order_col,
            **DEFAULT_SOCDEM_PARAMS,
        )


def _build_output_record(start_dt, end_dt, age_prb=0.0, income_code='C1', children_flg=False):
    return dict(
        utc_start_dt=start_dt,
        utc_end_dt=end_dt,
        age_segment_0_17_prb=age_prb,
        predict_socdem_income_code=income_code,
        has_children_wo_age_flg=children_flg,
        **DEFAULT_SOCDEM_PARAMS,
    )


_build_stream = lambda func: lambda records: [func(*r) for r in records]

build_init_input_stream = _build_stream(_build_init_input_record)
build_append_input_stream = _build_stream(_build_append_input_record)
build_output_stream = _build_stream(_build_output_record)
