import re
import json

import numpy as np
import pytest

from taxi_pyml.eats.places_ranking import view
from taxi_pyml.eats.places_ranking import external_data


class MockMLModel:
    @staticmethod
    def predict_proba(features_matrix):
        return np.zeros(shape=(len(features_matrix), len(features_matrix[0])))


class NotSupportedSortRanker:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, request, ids):
        raise view.NotSupportedSortError(self.name)


def mock_context_resources() -> view.ContextResources:
    return view.ContextResources(
        data_storage=None,
        personal_rec_models={
            view.DEFAULT_REC_MODEL: view.cxx.EmptyRecModel(),
            view.DEFAULT_PROMO_NEW_REC_MODEL: view.cxx.EmptyRecModel(),
            view.EMPTY_REC_MODEL: view.cxx.EmptyRecModel(),
        },
        places_rankers={
            view.DEFAULT_RANKER: view.cxx.HeuristicDefaultSortRanker(),
            view.DEFAULT_PROMO_NEW_RANKER: (
                view.cxx.HeuristicPromoNewSortRanker()
            ),
            view.DEFAULT_SORT_RANKER: view.cxx.HeuristicDefaultSortRanker(),
            view.FAST_DELIVERY_SORT_RANKER: (
                view.cxx.HeuristicEtaSortRanker()
            ),
            view.HIGH_RATING_SORT_RANKER: (
                view.cxx.HeuristicUserRatingSortRanker()
            ),
            view.CHEAP_FIRST_SORT_RANKER: NotSupportedSortRanker(
                'cheap_first',
            ),
            view.EXPENSIVE_FIRST_SORT_RANKER: NotSupportedSortRanker(
                'expensive_first',
            ),
        },
    )


class Resources:
    location_radius = 10
    min_order_rating = 4
    default_ranking_weight = 100
    min_ratings_count = 40
    user_rating_threshold = 4.0
    eta_group_minutes = 5
    average_rating_tolerance = 5.0
    candidates_extractors_params = {
        'fast_candidates_size': 10,
        'enable_orders': True,
    }
    features_extractors_params = {
        'use_candidate_ranks': True,
        'use_divisions': True,
    }
    post_processors_params = {}
    ml_model = MockMLModel


def test_creation_and_call(load):
    external_data.DataStorage.create_from_data_dir(
        data_dir='', allow_not_existing_files=True,
    )
    view.cxx.CombinationCandidatesExtractor(
        **Resources.candidates_extractors_params,
    )
    rec_model = view.cxx.EmptyRecModel()
    rec_model_params = view.cxx.RecModelParams(
        personal_block_size=2, personal_rec_model_name='cxx_v1_rec_model',
    )
    cxx_ranker = view.cxx.HeuristicDefaultSortRanker()
    builder = view.cxx.CatalogBuilder(
        rec_model, rec_model_params, cxx_ranker, 'test',
    )

    request = view.Types.Request.from_json(load('v1/request.json'))
    builder(request)


def test_cxx_candidates_extractor_v1(load):
    py_ce = view.cxx.CombinationCandidatesExtractor(
        **Resources.candidates_extractors_params,
    )
    cxx_ce = view.cxx.CombinationCandidatesExtractor(
        **Resources.candidates_extractors_params,
    )
    request = view.Types.Request.from_json(load('v1/request.json'))
    id_to_eta = {place.id: place.eta_minutes_min for place in request.places}
    assert sorted(map(id_to_eta.get, py_ce(request))) == sorted(
        map(id_to_eta.get, cxx_ce(request)),
    )


def test_matrix(load_json, load):
    candidates_extractor = view.cxx.CombinationCandidatesExtractor(
        **Resources.candidates_extractors_params,
    )
    features_extractor = view.cxx.FeaturesExtractorV1(
        **Resources.features_extractors_params,
    )

    request = view.Types.Request.from_json(load('v1/request.json'))
    true_matrix = load_json('v1/matrix.json')

    candidates = sorted(candidates_extractor(request))
    matrix = features_extractor(request, candidates)

    for vector, vector_true in zip(matrix, true_matrix):
        try:
            diff = np.array(vector) - np.array(vector_true)
        except Exception:
            for vector in matrix:
                print('VECTOR TEST:', vector)
                print()

        assert np.abs(diff).max() < 1e-3


def test_json_conversions(load):
    request = view.Types.Request.from_json(load('v1/request.json'))
    text = request.to_json()
    assert text == view.Types.Request.from_json(text).to_json()


def test_view_fallback_call(load, caplog):
    context_resources = mock_context_resources()
    request = view.Types.Request.from_json(load('v1/request.json'))
    response = view.handle(
        request=request,
        context_resources=context_resources,
        exp_list=[],
        time_storage=dict(),
        log_extra=None,
    )
    assert {place.id for place in response.result} == {
        place.id for place in request.places
    }
    assert re.findall('(ERROR|WARNING)', caplog.text) == ['ERROR', 'ERROR']


def test_view_sorts_fallback_default_high_rating_fast_delivery(load_json):
    context_resources = mock_context_resources()
    obj = load_json('v1/request.json')
    for sort in ['default', 'high_rating', 'fast_delivery']:
        obj['sort'] = sort
        request = view.Types.Request.from_json(json.dumps(obj))
        view.handle(
            request=request,
            context_resources=context_resources,
            exp_list=[],
            time_storage=dict(),
            log_extra=None,
        )


def test_view_sorts_fallback_assert_sorted(load_json):
    context_resources = mock_context_resources()
    obj = load_json('v1/request.json')
    id_to_place = {place['id']: place for place in obj['places']}
    for sort, sort_field in [
            # ('high_rating', 'average_user_rating'), FIXME
            ('fast_delivery', 'eta_minutes_min'),
    ]:
        obj['sort'] = sort
        request = view.Types.Request.from_json(json.dumps(obj))
        scores = [
            id_to_place[place.id].get(sort_field)
            for place in view.handle(
                request=request,
                context_resources=context_resources,
                exp_list=[],
                time_storage=dict(),
                log_extra=None,
            ).result
            if id_to_place[place.id]['is_available']
        ]
        assert scores == sorted(scores) or scores == sorted(
            scores, reverse=True,
        )


def calc_global_priority(place):
    result = False
    result |= place.is_new
    result |= place.user_ratings_count < Resources.min_ratings_count
    result |= place.ranking_weight > Resources.default_ranking_weight
    result |= (
        round(place.average_user_rating, 2) >= Resources.user_rating_threshold
    )
    return result


def get_simple_request(place_list_context='common', sort='default'):
    return view.Types.Request(
        user_id='',
        device_id='',
        request_id='request_id',
        ranking_at='2018-04-20T22:09:40+03:00',
        place_list_context=place_list_context,
        sort=sort,
        flags=[],
        user_agent='android',
        location=view.Types.GeoPoint(lon=1, lat=2),
        places=[
            view.Types.Place(
                id=1,
                brand_id=1,
                ranking_weight=100,
                eta_minutes_min=40,
                eta_minutes_max=50,
                cancel_rate=0.1,
                is_new=False,
                average_user_rating=4.8,
                shown_rating=4.8,
                user_ratings_count=50,
                is_available=True,
                available_at=None,
                delivery_type='',
                courier_type='pedestrian',
                brand='1',
                location=view.Types.GeoPoint(lon=7, lat=7),
                price_category_id=None,
                price_category=None,
                has_promo=None,
                delivery_cost=200,
                delivery_fee=view.Types.DeliveryFee(
                    surge_price=100,
                    thresholds=[
                        view.Types.DeliveryFeeThreshold(
                            base_price=100, lower_bound=200, upper_bound=None,
                        ),
                    ],
                ),
            ),
            view.Types.Place(
                id=2,
                brand_id=2,
                ranking_weight=100,
                eta_minutes_min=41,
                eta_minutes_max=51,
                cancel_rate=0.1,
                is_new=True,
                average_user_rating=4.3,
                shown_rating=4.5,
                user_ratings_count=50,
                is_available=True,
                available_at=None,
                delivery_type='',
                courier_type='pedestrian',
                brand='2',
                location=view.Types.GeoPoint(lon=6, lat=6),
                price_category_id=2,
                price_category=1,
                has_promo=True,
                delivery_cost=200,
                delivery_fee=view.Types.DeliveryFee(
                    surge_price=100,
                    thresholds=[
                        view.Types.DeliveryFeeThreshold(
                            base_price=100, lower_bound=200, upper_bound=None,
                        ),
                    ],
                ),
            ),
            view.Types.Place(
                id=5,
                brand_id=5,
                ranking_weight=100,
                eta_minutes_min=46,
                eta_minutes_max=56,
                cancel_rate=0.1,
                is_new=True,
                average_user_rating=4.4,
                shown_rating=4.4,
                user_ratings_count=50,
                is_available=True,
                available_at=None,
                delivery_type='',
                courier_type='pedestrian',
                brand='5',
                location=view.Types.GeoPoint(lon=6, lat=6),
                price_category_id=1,
                price_category=2,
                has_promo=True,
                delivery_cost=200,
                delivery_fee=view.Types.DeliveryFee(
                    surge_price=100,
                    thresholds=[
                        view.Types.DeliveryFeeThreshold(
                            base_price=100, lower_bound=200, upper_bound=None,
                        ),
                    ],
                ),
            ),
            view.Types.Place(
                id=6,
                brand_id=6,
                ranking_weight=100,
                eta_minutes_min=46,
                eta_minutes_max=56,
                cancel_rate=0.1,
                is_new=True,
                average_user_rating=4.4,
                shown_rating=None,
                user_ratings_count=50,
                is_available=True,
                available_at=None,
                delivery_type='',
                courier_type='pedestrian',
                brand='5',
                location=view.Types.GeoPoint(lon=6, lat=6),
                price_category_id=2,
                price_category=2,
                has_promo=False,
                delivery_cost=200,
                delivery_fee=view.Types.DeliveryFee(
                    surge_price=100,
                    thresholds=[
                        view.Types.DeliveryFeeThreshold(
                            base_price=100, lower_bound=200, upper_bound=None,
                        ),
                    ],
                ),
            ),
        ],
        orders=[
            view.Types.Order(
                id=7,
                order_nr='jf',
                status='delivered',
                place_id=2,
                place_location=view.Types.GeoPoint(6, 6),
                delivery_location=view.Types.GeoPoint(lon=1, lat=2),
                currency_code='rub',
                total_amount='',
                total_discounted_amount='',
                cancel_reason=None,
                feedback=None,
                is_asap=False,
                created_at='2018-04-20T22:09:40+03:00',
                confirmed_at='',
                remind_at=None,
                delivered_at='2',
            ),
            view.Types.Order(
                id=89,
                order_nr='jff',
                status='delivered',
                place_id=3,
                place_location=view.Types.GeoPoint(33, 32),
                delivery_location=view.Types.GeoPoint(lon=1, lat=2),
                currency_code='rub',
                total_amount='',
                total_discounted_amount='',
                cancel_reason=None,
                feedback=None,
                is_asap=False,
                created_at='2018-04-20T22:09:40+03:00',
                confirmed_at='',
                remind_at=None,
                delivered_at='2',
            ),
        ],
    )


@pytest.mark.skip(reason='this test flaps in different OS: TAXIML-4726 ')
def test_catalog_simple_request():
    rec_model = view.cxx.RecModelV1(
        features_extractor=view.cxx.FeaturesExtractorV1(
            **Resources.features_extractors_params,
        ),
        candidates_extractor=view.cxx.CombinationCandidatesExtractor(
            **Resources.candidates_extractors_params,
        ),
        predictions_extractor=view.cmodels.mock_catboost(159, 0),
        post_processor=view.cxx.DefaultPostProcessor(
            **Resources.post_processors_params,
        ),
    )
    cxx_ranker = view.cxx.HeuristicDefaultSortRanker()
    rec_model_params = view.cxx.RecModelParams(
        personal_block_size=2, personal_rec_model_name='cxx_v1_rec_model',
    )
    model = view.cxx.CatalogBuilder(
        rec_model, rec_model_params, cxx_ranker, 'test',
    )
    request = get_simple_request()
    assert (
        model(request).to_json()
        == view.Types.Response(
            request_id='request_id',
            provider='test',
            result=[
                view.Types.RankedPlace(
                    id=1, relevance=3, type='personal', position=0,
                ),
                view.Types.RankedPlace(
                    id=6, relevance=2, type='personal', position=1,
                ),
                view.Types.RankedPlace(
                    id=2, relevance=1, type='ranking', position=2,
                ),
                view.Types.RankedPlace(
                    id=5, relevance=0, type='ranking', position=3,
                ),
            ],
        ).to_json()
    )


def test_sorts_catalog_simple_request():
    rec_model = view.cxx.EmptyRecModel()
    request = get_simple_request()
    rec_model_params = view.cxx.RecModelParams(
        personal_block_size=1, personal_rec_model_name='cxx_v1_rec_model',
    )

    assert (
        view.cxx.CatalogBuilder(
            rec_model,
            rec_model_params,
            view.cxx.HeuristicEtaSortRanker(),
            'test',
        )(request).to_json()
        == view.Types.Response(
            request_id='request_id',
            provider='test',
            result=[
                view.Types.RankedPlace(
                    id=1, relevance=3, type='ranking', position=0,
                ),
                view.Types.RankedPlace(
                    id=2, relevance=2, type='ranking', position=1,
                ),
                view.Types.RankedPlace(
                    id=5, relevance=1, type='ranking', position=2,
                ),
                view.Types.RankedPlace(
                    id=6, relevance=0, type='ranking', position=3,
                ),
            ],
        ).to_json()
    )

    assert (
        view.cxx.CatalogBuilder(
            rec_model,
            rec_model_params,
            view.cxx.HeuristicUserRatingSortRanker(),
            'test',
        )(request).to_json()
        == view.Types.Response(
            request_id='request_id',
            provider='test',
            result=[
                view.Types.RankedPlace(
                    id=1, relevance=3, type='ranking', position=0,
                ),
                view.Types.RankedPlace(
                    id=2, relevance=2, type='ranking', position=1,
                ),
                view.Types.RankedPlace(
                    id=5, relevance=1, type='ranking', position=2,
                ),
                view.Types.RankedPlace(
                    id=6, relevance=0, type='ranking', position=3,
                ),
            ],
        ).to_json()
    )

    assert (
        view.cxx.CatalogBuilder(
            rec_model,
            rec_model_params,
            view.cxx.HeuristicCheapSortRanker(),
            'test',
        )(request).to_json()
        == view.Types.Response(
            request_id='request_id',
            provider='test',
            result=[
                view.Types.RankedPlace(
                    id=2, relevance=3, type='ranking', position=0,
                ),
                view.Types.RankedPlace(
                    id=5, relevance=2, type='ranking', position=1,
                ),
                view.Types.RankedPlace(
                    id=6, relevance=1, type='ranking', position=2,
                ),
                view.Types.RankedPlace(
                    id=1, relevance=0, type='ranking', position=3,
                ),
            ],
        ).to_json()
    )

    assert (
        view.cxx.CatalogBuilder(
            rec_model,
            rec_model_params,
            view.cxx.HeuristicExpensiveSortRanker(),
            'test',
        )(request).to_json()
        == view.Types.Response(
            request_id='request_id',
            provider='test',
            result=[
                view.Types.RankedPlace(
                    id=5, relevance=3, type='ranking', position=0,
                ),
                view.Types.RankedPlace(
                    id=6, relevance=2, type='ranking', position=1,
                ),
                view.Types.RankedPlace(
                    id=2, relevance=1, type='ranking', position=2,
                ),
                view.Types.RankedPlace(
                    id=1, relevance=0, type='ranking', position=3,
                ),
            ],
        ).to_json()
    )

    assert (
        view.cxx.CatalogBuilder(
            rec_model,
            rec_model_params,
            view.cxx.HeuristicPromoNewSortRanker(),
            'test',
        )(request).to_json()
        == view.Types.Response(
            request_id='request_id',
            provider='test',
            result=[
                view.Types.RankedPlace(
                    id=2, relevance=3, type='ranking', position=0,
                ),
                view.Types.RankedPlace(
                    id=5, relevance=2, type='ranking', position=1,
                ),
                view.Types.RankedPlace(
                    id=6, relevance=1, type='ranking', position=2,
                ),
                view.Types.RankedPlace(
                    id=1, relevance=0, type='ranking', position=3,
                ),
            ],
        ).to_json()
    )

    assert (
        view.cxx.CatalogBuilder(
            rec_model,
            rec_model_params,
            view.cxx.HeuristicNewPromoSortRanker(),
            'test',
        )(request).to_json()
        == view.Types.Response(
            request_id='request_id',
            provider='test',
            result=[
                view.Types.RankedPlace(
                    id=2, relevance=3, type='ranking', position=0,
                ),
                view.Types.RankedPlace(
                    id=5, relevance=2, type='ranking', position=1,
                ),
                view.Types.RankedPlace(
                    id=6, relevance=1, type='ranking', position=2,
                ),
                view.Types.RankedPlace(
                    id=1, relevance=0, type='ranking', position=3,
                ),
            ],
        ).to_json()
    )


def test_features_extractor_v1():
    candidates_extractor = view.cxx.CombinationCandidatesExtractor(
        **Resources.candidates_extractors_params,
    )
    fe_1 = view.cxx.FeaturesExtractorV1(
        use_divisions=False, use_candidate_ranks=False,
    )
    fe_2 = view.cxx.FeaturesExtractorV1(
        use_divisions=True, use_candidate_ranks=False,
    )
    fe_3 = view.cxx.FeaturesExtractorV1(
        use_divisions=False, use_candidate_ranks=True,
    )
    fe_4 = view.cxx.FeaturesExtractorV1(
        use_divisions=True, use_candidate_ranks=True,
    )
    request = get_simple_request()
    candidates = sorted(candidates_extractor(request))
    matrix_1 = fe_1(request, candidates)
    matrix_2 = fe_2(request, candidates)
    matrix_3 = fe_3(request, candidates)
    matrix_4 = fe_4(request, candidates)

    assert len(matrix_1) == len(matrix_2)
    assert len(matrix_1) == len(matrix_3)
    assert len(matrix_1) == len(matrix_4)
    assert len(matrix_1) == 4
    assert len(matrix_1[0]) == 85
    assert len(matrix_2[0]) == 145
    assert len(matrix_3[0]) == 99
    assert len(matrix_4[0]) == 159

    with pytest.raises(ValueError):
        fe_1(request, [-1])

    assert len(fe_1(request, candidates, indices=[0] * 1000)) == 1000
