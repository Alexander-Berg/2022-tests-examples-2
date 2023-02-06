#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/geosuggest/auto_position/v1/objects.hpp>
#include <ml/geosuggest/auto_position/v1/rec_sys/candidates_extractor.hpp>
#include <ml/geosuggest/auto_position/v1/resource.hpp>
#include <ml/geosuggest/common/objects.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::geosuggest::auto_position::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("geosuggest_auto_position_v1");
}  // namespace

TEST(AutoPositionV1, extractors) {
  const auto recommender_config = ml::common::FromJsonString<RecommenderConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));

  const auto features_config = recommender_config.features_config;
  const auto candidates_config = recommender_config.candidates_config;
  ASSERT_EQ(features_config.last_searchroutes_count, 0ul);
  ASSERT_EQ(features_config.last_orders_count, 10ul);
  ASSERT_EQ(features_config.geo_combinations_count, 5ul);
  ASSERT_EQ(features_config.time_shifts_count, 3ul);
  ASSERT_EQ(features_config.coord_provider_types.size(), 4ul);
  ASSERT_EQ(features_config.state_field_types.size(), 2ul);
  ASSERT_FALSE(features_config.use_aggregators);
  ASSERT_EQ(features_config.order_counts_config.max_distances.size(), 0ul);
  ASSERT_EQ(features_config.order_counts_config.max_days.size(), 0ul);
  ASSERT_EQ(features_config.order_counts_config.max_hours.size(), 0ul);
  ASSERT_FALSE(features_config.order_counts_config.use_text);

  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const CandidatesExtractor candidates_extractor(
      recommender_config.candidates_config);
  const auto candidates = candidates_extractor.Apply(request);
  ASSERT_EQ(candidates.size(), 2ul);
  const FeaturesExtractor features_extractor(
      recommender_config.features_config);
  const auto features = features_extractor.Apply(candidates, request);
  ASSERT_EQ(features.numerical.size(), 2ul);
  ASSERT_EQ(features.categorical.size(), 2ul);
  ASSERT_EQ(features.numerical[0].size(), features.numerical_size);
  ASSERT_EQ(features.categorical[0].size(), features.categorical_size);
  ASSERT_EQ(features.numerical[0].size(), 131ul);
  ASSERT_EQ(features.categorical[0].size(), 5ul);
}

TEST(AutoPositionV1, extractors_second_iteration) {
  const auto recommender_config = ml::common::FromJsonString<RecommenderConfig>(
      ml::common::ReadFileContents(kTestDataDir +
                                   "/resource_second_iteration/config.json"));

  const auto features_config = recommender_config.features_config;
  ASSERT_EQ(features_config.last_searchroutes_count, 5ul);
  ASSERT_EQ(features_config.last_orders_count, 10ul);
  ASSERT_EQ(features_config.geo_combinations_count, 5ul);
  ASSERT_EQ(features_config.time_shifts_count, 3ul);
  ASSERT_EQ(features_config.coord_provider_types.size(), 4ul);
  ASSERT_EQ(features_config.state_field_types.size(), 2ul);
  ASSERT_TRUE(features_config.use_aggregators);
  ASSERT_EQ(features_config.order_counts_config.max_distances.size(), 3ul);
  ASSERT_EQ(features_config.order_counts_config.max_days.size(), 3ul);
  ASSERT_EQ(features_config.order_counts_config.max_hours.size(), 2ul);

  const auto candidates_config = recommender_config.candidates_config;
  ASSERT_FLOAT_EQ(candidates_config.GetMethodConfig("search_routes.destination")
                      .max_distance,
                  1400000.0);
  ASSERT_TRUE(features_config.order_counts_config.use_text);

  const auto request =
      ml::common::FromJsonString<Request>(ml::common::ReadFileContents(
          kTestDataDir + "/request_second_iteration.json"));
  ASSERT_EQ(request.search_routes.size(), 1ul);
  const CandidatesExtractor candidates_extractor(
      recommender_config.candidates_config);
  const auto candidates = candidates_extractor.Apply(request);
  ASSERT_EQ(candidates.size(), 6ul);
  const FeaturesExtractor features_extractor(
      recommender_config.features_config);
  const auto features = features_extractor.Apply(candidates, request);
  ASSERT_EQ(features.numerical.size(), 6ul);
  ASSERT_EQ(features.categorical.size(), 6ul);
  ASSERT_EQ(features.numerical[0].size(), features.numerical_size);
  ASSERT_EQ(features.categorical[0].size(), features.categorical_size);
  ASSERT_EQ(features.numerical[0].size(), 351ul);
  ASSERT_EQ(features.categorical[0].size(), 5ul);
}

TEST(AutoPositionV1, recommender) {
  Resource resource(kTestDataDir + "/resource", true);
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto recommender = resource.GetRecommender();
  Params params;

  params.exploration_mode = true;
  auto response = recommender->Apply(request, params);
  ASSERT_TRUE(response.selected_candidate);
  ASSERT_EQ(response.candidates.size(), 2ul);

  params.exploration_mode = false;
  response = recommender->Apply(request, params);
  ASSERT_TRUE(response.selected_candidate);
  ASSERT_EQ(response.candidates.size(), 2ul);
}

TEST(AutoPositionV1, userplace_recommender) {
  Resource resource(kTestDataDir + "/resource", true);
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto recommender = resource.GetRecommender();
  Params params;
  params.max_userplace_distance = 100;
  const auto response = recommender->Apply(request, params);
  ASSERT_EQ(response.selected_candidate->userplace->id, "up_work");
  ASSERT_EQ(*response.selected_candidate->comment, "Заезд во двор");
  ASSERT_EQ(*response.selected_candidate->comment_courier,
            "comment for courier");
}

TEST(AutoPositionV1, extra_data_for_commented_candidate) {
  Resource resource(kTestDataDir + "/resource", true);
  const auto request =
      ml::common::FromJsonString<Request>(ml::common::ReadFileContents(
          kTestDataDir + "/request_for_fetching_extra_data.json"));

  const auto recommender = resource.GetRecommender();
  Params params;
  params.extra_data_history_radius = 10.0;
  params.source_history_comments_radius = 10.0;
  const auto response = recommender->Apply(request, params);
  const auto s = ml::common::ToJsonString<Response>(response);

  ASSERT_EQ(response.selected_candidate->geoaddress.personal_phone_id, "123");
  ASSERT_EQ(response.selected_candidate->geoaddress.floor_number, "2");
  ASSERT_EQ(response.selected_candidate->geoaddress.doorphone_number, "24");
  ASSERT_EQ(response.selected_candidate->geoaddress.entrance, "4");
  ASSERT_EQ(response.selected_candidate->geoaddress.quarters_number, "24");
  ASSERT_EQ(response.selected_candidate->geoaddress.short_text,
            "Садовническая ул., 82с2");
  ASSERT_EQ(response.selected_candidate->geoaddress.full_text,
            "Россия, Москва, Садовническая улица, 82с2");
  ASSERT_EQ(response.selected_candidate->comment, "comment_test");
}
