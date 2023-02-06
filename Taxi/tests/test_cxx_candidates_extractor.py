import json

from taxi_ml_cxx.zoo.expected_sources import CandidatesExtractor


if __name__ == '__main__':
    with open('body.json', 'r') as body_file:
        body = json.load(body_file)

    extractors = {
        'sources_ex': CandidatesExtractor(
            max_candidates=20, geo_precision=1, use_pin_position=False,
            use_user_location=False, use_sources=True, use_destinations=False,
            use_completion_points=False, use_adjusted_sources=False
        ),
        'pin_sources_ex': CandidatesExtractor(
            max_candidates=20, geo_precision=5, use_pin_position=True,
            use_user_location=False, use_sources=True, use_destinations=False,
            use_completion_points=False, use_adjusted_sources=False
        ),
        'all_ex': CandidatesExtractor(
            max_candidates=20, geo_precision=5, use_pin_position=True,
            use_user_location=False, use_sources=True, use_destinations=True,
            use_completion_points=True, use_adjusted_sources=True
        )
    }
    for name, extractor in extractors.iteritems():
        with open('{}_candidates.json'.format(name), 'r') as candidates_file:
            assert json.load(candidates_file) == extractor(body)
    print('Test OK')
