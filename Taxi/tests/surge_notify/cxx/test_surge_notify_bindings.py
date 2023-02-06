from ctaxi_pyml.surge_notify import v1 as cxx
from pytest import approx


def test_extractors(load, load_json):
    request = cxx.Request.from_json(load('request.json'))
    fs = cxx.FeatureStorage(request, ['econom'])
    assert len(fs.GetNumFeats()[0]) == 110, len(fs.GetNumFeats()[0])
    assert len(fs.GetCatFeats()[0]) == 4, len(fs.GetNumFeats()[0])

    feats_example = load_json('features.json')

    assert fs.GetNumFeats()[0] == approx(feats_example['num'])
    assert fs.GetCatFeats()[0] == feats_example['cat']
