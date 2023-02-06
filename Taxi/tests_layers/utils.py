import operator


def sort_features(feature_collection):
    feature_collection['features'].sort(key=operator.itemgetter('id'))
    return feature_collection
