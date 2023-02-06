# coding: utf-8

from business_models.cohorts import Cohort
from business_models.util import change_coding
from .common import read_data, check_df, write_data


def get_cohorts_tests():
    data = read_data(__file__, 'data.pkl')
    models = ['incremental_retention', 'regular_retention']
    kwargs = {'value_name': 'trips', 'scale': 'month'}

    for retention_model in models:
        cohort = Cohort(retention_model=retention_model)
        golden = read_data(__file__, 'get_cohort_no_future.pkl')
        result = cohort.get_cohorts(data, **kwargs)
        check_df(change_coding(golden), change_coding(result), obj=retention_model)
        for future in ['', '12']:
            future_dots = int(future) if future != '' else 0
            golden = read_data(__file__, 'get_cohort_%s_future%s.pkl' % (retention_model.split('_')[0], future))
            result = cohort.get_cohorts(data, predict_future=True,
                                        cohort_len=future_dots if future_dots != 0 else None,
                                        **kwargs)
            check_df(change_coding(golden), change_coding(result),
                     obj='get_cohorts for retention_model "%s" with future dots "%d" ' % (retention_model, future_dots))
