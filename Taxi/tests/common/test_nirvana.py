"""
This is manual running test to check Nirvana API

Need no errors. After this script you should find:
- new new_catboost.cbm in //home/taxi_ml/dev/nirvana/tools_test_data
- new prediction_1 in //home/taxi_ml/dev/nirvana/tools_test_data
- new prediction_2 in //home/taxi_ml/dev/nirvana/tools_test_data
"""

from taxi.ml.nirvana.common.nirvana.actions import (
    CatboostAction,
    get_catboost_yt_format,
    CloneSetParamsAndLaunchAction,
)
from taxi.ml.nirvana.common.nirvana.pool import NirvanaPool

PATH_YT_DATASET = '//home/taxi_ml/dev/nirvana/tools_test_data/{}'
WORKFLOW_ID = '96d4bae3-c11e-4855-8ab2-746024fa30de'


if __name__ == '__main__':
    nirvana_pool = NirvanaPool(verbose=True)
    nirvana_pool.process(
        [
            # clone graph and run
            CloneSetParamsAndLaunchAction(
                base_instance_id='7578a66f-507f-4fb7-ba2f-a4bf3452b059',
                param_values=[
                    {'parameter': 'test_param', 'value': 'param_value'},
                ],
                description='test_clone',
            ),
            # train and save model
            CatboostAction(
                workflow_id=WORKFLOW_ID,
                train_path=PATH_YT_DATASET.format('train'),
                validation_path=PATH_YT_DATASET.format('test'),
                test_path=PATH_YT_DATASET.format('test'),
                yt_model_path=PATH_YT_DATASET.format('new_catboost.cbm'),
                output_path=PATH_YT_DATASET.format('prediction_1'),
                resources_dir='./tmp/',
                use_gpu=True,
                iterations=200,
                od_pval=1e-2,
                loss_function='MAE',
                experiment_description='test_train_and_apply',
                max_ctr_complexity=1.0,
                catboost_yt_pool_format=get_catboost_yt_format(
                    ignore_columns=[2, 3], categorical_columns=[54, 55],
                ),
                catboost_yt_output_format=['DocId', 'RawFormulaVal'],
            ),
            # apply model
            CatboostAction(
                workflow_id=WORKFLOW_ID,
                test_path=PATH_YT_DATASET.format('test'),
                yt_model_path=PATH_YT_DATASET.format('catboost.cbm'),
                output_path=PATH_YT_DATASET.format('prediction_2'),
                experiment_description='test_apply',
                catboost_yt_pool_format=get_catboost_yt_format(
                    ignore_columns=[2, 3], categorical_columns=[54, 55],
                ),
                catboost_yt_output_format=['DocId', 'RawFormulaVal'],
            ),
        ],
    )
