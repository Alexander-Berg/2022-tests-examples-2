# import os
# import uuid
#
# import catboost
# import pytest
# from cprojects.examples import catboost_usage
# from scipy.special import expit
#
#
# def test_configure_environment():
#     train_data = [[0, 1, 3], [1, 2, 3], [2, 1, 1], [2, 1, 1]]
#     target_data = [0, 1, 0, 1]
#     model = catboost.CatBoostClassifier().fit(
#         train_data, target_data, verbose=False,
#     )
#     path = str(uuid.uuid4())
#     try:
#         model.save_model(path)
#
#         with pytest.raises(RuntimeError):
#             catboost_usage(path, [[1, 2]])
#
#         vec = [2, 3, 4]
#         assert model.predict(
#             vec, prediction_type='Probability', verbose=False,
#         )[1] == expit(catboost_usage(path, [vec])[0])
#     finally:
#         os.remove(path)
