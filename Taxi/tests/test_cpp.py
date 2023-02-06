import json

from taxi_ml_cxx.zoo.personal_conversion import FeaturesExtractor


with open('data.json', 'r') as f:
    data = json.load(f)

extractor = FeaturesExtractor()
output = extractor(data)
features = data['num_features'] + data['cat_features']

for i in range(len(features)):
    if isinstance(features[i], float):
        assert abs(features[i] - output[i]) < 1e-32
    else:
        assert features[i] == output[i]

print('Test OK')
