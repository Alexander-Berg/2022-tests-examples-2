import pytest
from nile.api.v1 import Record


def test_candidates_selection():
    import catboost
    model = catboost.CatBoostClassifier(
        verbose=False, allow_writing_files=False,
    ).fit([[1, 2], [2, 3]], [1, 0])
    model.set_feature_names(['a', 'b'])
    with pytest.raises(catboost.CatBoostError):
        model.predict(Record(a=1, b=2))
    from taxi.ml.nirvana.common.patched_catboost import CatBoostClassifier
    pred1 = model.predict(Record(a=1, b=2))
    pred2 = model.predict([Record(a=1, b=2), Record(a=1, b=2)])
    assert CatBoostClassifier == catboost.CatBoostClassifier
    assert (pred2 == [pred1, pred1]).all()
