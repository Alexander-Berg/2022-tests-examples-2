import os

from projects.eats.places_ranking.rec_sys.factory import RecFactory


def test_factory_create_methods():
    factory = RecFactory(
        personal_rec_model_dir='.',
        static_resources_dir='.',
        ds_allow_not_existing_files=True,
        features_extractors_params={
            'use_divisions': True,
            'use_candidate_ranks': False,
        },
        candidates_extractors_params={
            'enable_orders': True,
            'fast_candidates_size': 10,
        },
        post_processors_params={},
        pe_load='mock',
        predictions_extractors_params={
            'num_factors_count': 0,
            'cat_factors_count': 0,
        },
        personal_rec_model_params={
            'personal_block_size': 4,
            'personal_rec_model_name': 'cxx_v1_rec_model',
        },
    )

    os.environ.pop('NILE_IS_RUNNING_ON_CLUSTER')

    factory.create_request_parser()
    factory.create_candidates_extractor()
    factory.create_targets_extractor()
    factory.create_sampler()
    factory.create_features_extractor()
    factory.create_post_processor()
    factory.create_rec_model()
