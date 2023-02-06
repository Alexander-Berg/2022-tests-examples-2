#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/geosuggest/address_suggest/v1/fallback.hpp>
#include <ml/geosuggest/address_suggest/v1/objects.hpp>
#include <ml/geosuggest/address_suggest/v1/rec_sys/candidates_extractor.hpp>
#include <ml/geosuggest/address_suggest/v1/rec_sys/features_extractor.hpp>
#include <ml/geosuggest/address_suggest/v1/rec_sys/popular_locations/candidates_extractor.hpp>
#include <ml/geosuggest/address_suggest/v1/rec_sys/popular_locations/features_extractor.hpp>
#include <ml/geosuggest/address_suggest/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::geosuggest;
using namespace ml::geosuggest::address_suggest::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("geosuggest_address_suggest_v1");

Params create_default_recommender_params() {
  Params params;
  params.max_top_size = 3;
  params.max_middle_size = 20;
  params.max_bottom_size = 20;
  params.max_total_size = 20;
  params.top_merge_distance = 200;
  params.top_merge_texts = true;
  params.userplace_merge_distance = 200;
  params.userplace_merge_texts = false;
  params.bottom_merge_distance = 200;
  params.bottom_merge_texts = true;
  params.min_probability = 0.0;
  params.equal_probability_diff = 0.00000001;
  params.methods = {"userplace", "phone_history.destination",
                    "phone_history.intermediate", "phone_history.source",
                    "phone_history.completion_point"};
  params.min_center_distance = 10;
  params.max_center_distance = 100000;
  params.userplace_exclusive_radius = 1;
  return params;
}

Request create_request(std::string&& end_path = "/request.json") {
  return ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + std::move(end_path)));
}

std::pair<Request, RecommenderConfig> load_personal_data(
    const std::string& resource_dir) {
  auto request = create_request();
  auto config = ml::common::FromJsonString<RecommenderConfig>(
      ml::common::ReadFileContents(resource_dir + "/personal_config.json"));
  return {request, config};
}

std::pair<Request, popular_locations::RecommenderConfig> load_popular_data() {
  auto request = create_request();
  auto popular_locations = ml::common::FromJsonString<PopularLocationsStorage>(
      ml::common::ReadFileContents(kTestDataDir +
                                   "/resource/popular_locations_storage.json"));
  request.popular_locations = popular_locations.items;
  auto config =
      ml::common::FromJsonString<popular_locations::RecommenderConfig>(
          ml::common::ReadFileContents(kTestDataDir +
                                       "/resource/popular_config.json"));
  return {request, config};
}
}  // namespace

TEST(AddressSuggestV1, extract_new_candidate) {
  auto [request, config] = load_personal_data(kTestDataDir + "/resource");
  request = create_request("/request_with_personal_suggest.json");
  ASSERT_EQ(request.suggest_addresses.size(), 1ul);
  auto candidates_extractor = CandidatesExtractor(config.candidates_config);
  auto candidates = candidates_extractor.Apply(request);
  ASSERT_EQ(candidates.size(), 1ul);
  const auto& num_features =
      candidates.front().personal_geosuggest_num_features;
  ASSERT_TRUE(num_features);
  ASSERT_EQ(num_features->size(), 1ul);
  auto it = num_features->find("personal_result_from_user_sessions");
  ASSERT_NE(it, num_features->end());
  ASSERT_EQ(it->second, 1.5);
  const auto& cat_features =
      candidates.front().personal_geosuggest_cat_features;
  ASSERT_TRUE(cat_features);
  ASSERT_EQ(cat_features->size(), 0ul);
}

TEST(AddressSuggestV1, take_personal_geosuggest_features) {
  auto [request, config] =
      load_personal_data(kTestDataDir + "/personal_suggest");
  request =
      create_request("/request_with_personal_suggest_sharing_features.json");
  ASSERT_EQ(request.suggest_addresses.size(), 2ul);
  ASSERT_EQ(request.userplaces.size(), 3ul);
  auto candidates_extractor = CandidatesExtractor(config.candidates_config);
  const auto features_extractor = FeaturesExtractor(config.features_config);
  auto candidates = candidates_extractor.Apply(request);
  const auto features = features_extractor.Apply(candidates, request);
  ASSERT_EQ(candidates.size(), 4ul);
  ASSERT_EQ(features.numerical_size, 349ul);
  ASSERT_EQ(features.numerical[0][88], 123123123);
  ASSERT_LE(features.numerical[1][88], 1);
  ASSERT_EQ(features.numerical[2][88], 321321321);
  ASSERT_EQ(features.numerical[3][88], 123123123);
}

TEST(AddressSuggestV1, extractors) {
  auto [request, config] = load_personal_data(kTestDataDir + "/resource");
  const auto& features_config = config.features_config;
  ASSERT_EQ(features_config.state_field_types.size(), 2ul);
  ASSERT_EQ(features_config.time_shifts_count, 3ul);
  ASSERT_EQ(features_config.coord_provider_types.size(), 5ul);
  ASSERT_EQ(features_config.last_orders_count, 5ul);
  ASSERT_EQ(features_config.last_searchroutes_count, 5ul);
  ASSERT_EQ(features_config.order_counts_config.max_distances.size(), 4ul);
  ASSERT_EQ(features_config.order_counts_config.max_days.size(), 3ul);
  ASSERT_EQ(features_config.order_counts_config.max_hours.size(), 2ul);
  ASSERT_TRUE(features_config.order_counts_config.use_text);
  ASSERT_EQ(features_config.searchroutes_counts_config.max_distances.size(),
            4ul);
  ASSERT_EQ(features_config.searchroutes_counts_config.max_days.size(), 1ul);
  ASSERT_EQ(features_config.searchroutes_counts_config.max_hours.size(), 2ul);
  ASSERT_TRUE(features_config.searchroutes_counts_config.use_text);

  auto candidates_extractor = CandidatesExtractor(config.candidates_config);
  const auto features_extractor = FeaturesExtractor(config.features_config);
  auto candidates = candidates_extractor.Apply(request);
  const auto features = features_extractor.Apply(candidates, request);
  ASSERT_EQ(candidates.size(), 6ul);
  ASSERT_EQ(features.numerical.size(), 6ul);
  ASSERT_EQ(features.categorical.size(), 6ul);
  ASSERT_EQ(features.categorical[0].size(), 5ul);
  ASSERT_EQ(features.numerical[0].size(), 349ul);

  config.candidates_config.merge_userplaces = true;
  candidates_extractor = CandidatesExtractor(config.candidates_config);
  candidates = candidates_extractor.Apply(request);
  ASSERT_EQ(candidates.size(), 5ul);

  config.candidates_config.merge_use_texts = false;
  candidates_extractor = CandidatesExtractor(config.candidates_config);
  candidates = candidates_extractor.Apply(request);
  ASSERT_EQ(candidates.size(), 7ul);
}

TEST(AddressSuggestV1, postprocessor) {
  auto [request, config] = load_personal_data(kTestDataDir + "/resource");
  config.candidates_config.merge_use_texts = false;
  const auto candidates_extractor =
      CandidatesExtractor(config.candidates_config);
  request.userplaces.at(1).geoaddress.geopoint =
      ml::common::GeoPoint(69.27, 41.29);
  const auto candidates = candidates_extractor.Apply(request);

  std::vector<double> predictions{0.99, 0.98, 0.69, 0.50,
                                  0.38, 0.22, 0.17, 0.12};

  auto params = create_default_recommender_params();
  const auto postprocessor = PostProcessor();
  auto response = postprocessor.Apply(candidates, predictions, request, params);
  ASSERT_EQ(response.size(), 4ul);
  for (const auto& item : response) {
    ASSERT_TRUE(item.probability.has_value());
    ASSERT_GT(item.probability.value(), 0.);
  }
  params.bottom_merge_texts = false;
  response = postprocessor.Apply(candidates, predictions, request, params);
  ASSERT_EQ(response.size(), 5ul);
}

TEST(AddressSuggestV1, postprocessor_no_searches) {
  auto [request, config] =
      load_personal_data(kTestDataDir + "/no_searchroutes_resource");
  config.candidates_config.merge_use_texts = false;
  const auto candidates_extractor =
      CandidatesExtractor(config.candidates_config);
  request.userplaces.at(1).geoaddress.geopoint =
      ml::common::GeoPoint(69.27, 41.29);
  const auto candidates = candidates_extractor.Apply(request);

  std::vector<double> predictions{0.99, 0.98, 0.69, 0.50, 0.38};

  auto params = create_default_recommender_params();
  const auto postprocessor = PostProcessor();
  auto response = postprocessor.Apply(candidates, predictions, request, params);
  ASSERT_EQ(response.size(), 4ul);
  params.bottom_merge_texts = false;
  response = postprocessor.Apply(candidates, predictions, request, params);
  ASSERT_EQ(response.size(), 5ul);
}

TEST(AddressSuggestV1, fallback) {
  const auto request = create_request();
  const auto recommender = RecommenderFallback();
  Params params;
  params.max_total_size = 1;
  const auto response = recommender.Apply(request, params);
  ASSERT_EQ(response.items.size(), 1ul);
}

TEST(AddressSuggestV1, resource) {
  auto params = create_default_recommender_params();
  params.max_popular_locations_size = 10;
  params.popular_locations_min_probability = 0.0;
  auto request = create_request();
  auto popular_locations = ml::common::FromJsonString<PopularLocationsStorage>(
      ml::common::ReadFileContents(kTestDataDir +
                                   "/resource/popular_locations_storage.json"));
  request.popular_locations = popular_locations.items;

  Resource resource(kTestDataDir + "/resource", true);
  const auto recommender_ptr = resource.GetRecommender();
  const auto response = recommender_ptr->Apply(request, params);

  ASSERT_GT(response.items.size(), 0ul);
  ASSERT_EQ(response.popular_items.size(), 0ul);
}

TEST(AddressSuggestV1, resource_no_searches) {
  auto params = create_default_recommender_params();
  const auto request = create_request();
  Resource resource(kTestDataDir + "/no_searchroutes_resource", true);
  const auto recommender_ptr = resource.GetRecommender();
  const auto response = recommender_ptr->Apply(request, params);
}

TEST(PopularLocationsV1, extractors) {
  auto [request, config] = load_popular_data();
  ASSERT_EQ(request.popular_locations.size(), 1ul);

  const popular_locations::CandidatesExtractor candidates_extractor(
      config.candidates_config);
  const popular_locations::FeaturesExtractor features_extractor(
      config.features_config);

  const auto candidates = candidates_extractor.Apply(request);
  ASSERT_EQ(candidates.size(), 1ul);
  const auto features = features_extractor.Apply(candidates, request);
}

TEST(PopularLocationsV1, recommender) {
  auto [request, config] = load_popular_data();
  ASSERT_EQ(request.popular_locations.size(), 1ul);

  Params popular_params;
  popular_params.max_total_size = 10;
  popular_params.max_center_distance = 10000000;
  popular_params.max_popular_locations_size = 10;
  popular_params.popular_locations_min_probability = 0.0;
  const auto postprocessor = popular_locations::PostProcessor();
  auto postprocessor_res =
      postprocessor.Apply(request.popular_locations, std::vector<double>{5},
                          request, popular_params);
  ASSERT_EQ(postprocessor_res.size(), 1ul);
  popular_params.popular_locations_min_probability = 0.7;
  postprocessor_res =
      postprocessor.Apply(request.popular_locations, std::vector<double>{-4},
                          request, popular_params);
  ASSERT_EQ(postprocessor_res.size(), 0ul);

  postprocessor_res =
      postprocessor.Apply(request.popular_locations, std::vector<double>{17},
                          request, popular_params);

  const auto config_path = kTestDataDir + "/resource/popular_config.json";
  const auto model_path = "";

  const auto popular_recommender =
      CreatePopularRecommender(config_path, model_path, true);
  const auto result = popular_recommender->Apply(request, popular_params);
  ASSERT_EQ(result.items.size(), 0ul);
}

TEST(AddressSuggestV1, history_comments) {
  auto candidate = Candidate::FromGeoAddress(
      GeoAddress::FromGeoPoint({69.2724, 41.2990}), "method");
  Params params;
  params.max_total_size = 1;
  params.max_top_size = 1;
  params.methods = {"method"};
  params.max_center_distance = 100000;
  params.source_history_comments_radius = 100;
  auto request = create_request();
  request.point_type = "a";
  const auto results = PostProcessor().Apply({candidate}, {0}, request, params);
  ASSERT_EQ(results.size(), 1ul);
  ASSERT_EQ(*results[0].comment, "комментарий на узбекском");
}

TEST(AddressSuggestV1, delivery_hack) {
  const auto delivery_request = create_request("/delivery/request.json");
  ASSERT_TRUE(delivery_request.app_state.current_mode.has_value());
  ASSERT_EQ(*delivery_request.app_state.current_mode, "delivery");

  auto recommender_config = ml::common::FromJsonString<RecommenderConfig>(
      ml::common::ReadFileContents(kTestDataDir +
                                   "/delivery/personal_config.json"));
  auto candidates_config = recommender_config.candidates_config;
  ASSERT_EQ(candidates_config.merge_tariffs.size(), 2ul);
  ASSERT_EQ(candidates_config.delivery_mode_name, "delivery");

  const auto candidates_extractor = CandidatesExtractor(candidates_config);
  const auto candidates = candidates_extractor.Apply(delivery_request);
  ASSERT_EQ(candidates.size(), 8ul);

  candidates_config.merge_tariffs = {};
  const auto candidates_extractor2 = CandidatesExtractor(candidates_config);
  const auto candidates2 = candidates_extractor2.Apply(delivery_request);
  ASSERT_EQ(candidates2.size(), 6ul);

  const auto default_params = create_default_recommender_params();

  Resource resource(kTestDataDir + "/delivery", true);
  const auto recommender_ptr = resource.GetRecommender();
  const auto response =
      recommender_ptr->Apply(delivery_request, default_params);
  ASSERT_EQ(response.items.size(), 3ul);
  ASSERT_TRUE(response.items[0].IsUserplace());
  ASSERT_TRUE(response.items[1].tariff_class);
  ASSERT_EQ(*response.items[1].tariff_class, "econom");

  auto delivery_params = default_params;
  delivery_params.delivery_tariff_classes = {"express", "courier"};
  delivery_params.delivery_bonus = 0.3;
  const auto delivery_response =
      recommender_ptr->Apply(delivery_request, delivery_params);
  ASSERT_EQ(delivery_response.items.size(), 3ul);
  ASSERT_FALSE(delivery_response.items[0].IsUserplace());
  ASSERT_TRUE(delivery_response.items[0].tariff_class);
  ASSERT_EQ(*delivery_response.items[0].tariff_class, "express");
}
