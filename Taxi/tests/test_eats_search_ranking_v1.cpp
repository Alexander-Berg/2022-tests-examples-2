#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/eats/catalog/resources/v1.hpp>
#include <ml/eats/search_ranking/resources/v1/model_resource.hpp>
#include <ml/eats/search_ranking/resources/v1/ranker/ranker.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("eats_search_ranking_v1");
}  // namespace

TEST(EatsSearchRankingObjectsV1, MLRequest_unpacking) {
  auto request = ml::common::FromJsonString<
      ml::eats::search_ranking::views::v1::MLRequest>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));

  ASSERT_EQ(request, ml::common::FromJsonString<
                         ml::eats::search_ranking::views::v1::MLRequest>(
                         ml::common::ToJsonString(request)));

  ASSERT_EQ(request.candidates.size(), 3);
  ASSERT_EQ(request.text_query, "покешная");
}

TEST(EatsSearchRankingFeatureExtractorV1, feature_extractor) {
  auto request = ml::common::FromJsonString<
      ml::eats::search_ranking::views::v1::MLRequest>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));

  auto static_resource =
      ml::eats::catalog::resources::v1::LoadStaticResourcesFromDir(
          kTestDataDir + "/static");
  auto dish_stats_resource =
      ml::eats::dishes_statistics::resources::v1::LoadStaticResourcesFromDir(
          kTestDataDir + "/static");
  auto static_mappings =
      ml::eats::suggest::mappings::v1::LoadStaticMappingsFromDir(kTestDataDir +
                                                                 "/static");
  auto feature_extractor = ml::eats::search_ranking::resources::v1::ranker::
      LoadFeaturesExtractorFromDir(kTestDataDir + "/model");

  auto features = feature_extractor.Apply(request, static_resource,
                                          dish_stats_resource, static_mappings);
  auto categorical = features.categorical;
  auto numerical = features.numerical;

  ASSERT_EQ(categorical.size(), 3ul);
  ASSERT_EQ(numerical.size(), 3ul);
  ASSERT_EQ(categorical[0].size(), 0ul);
  ASSERT_EQ(numerical[0].size(), 22ul);
}

TEST(EatsSearchRankingPredictor, predictor) {
  auto request = ml::common::FromJsonString<
      ml::eats::search_ranking::views::v1::MLRequest>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  auto static_resource =
      ml::eats::catalog::resources::v1::LoadStaticResourcesFromDir(
          kTestDataDir + "/static");
  auto dish_stats_resource =
      ml::eats::dishes_statistics::resources::v1::LoadStaticResourcesFromDir(
          kTestDataDir + "/static");
  auto static_mappings =
      ml::eats::suggest::mappings::v1::LoadStaticMappingsFromDir(kTestDataDir +
                                                                 "/static");

  ml::eats::search_ranking::resources::v1::ranker::EatsSearchRankingExpParams
      params = {};
  bool mock_mode = true;
  auto predictor =
      ml::eats::search_ranking::resources::v1::model_resource::LoadRanker(
          "mock", kTestDataDir + "/model", mock_mode);

  ASSERT_NO_THROW(predictor->Apply(request, params, static_resource,
                                   dish_stats_resource, static_mappings));

  auto response = predictor->Apply(request, params, static_resource,
                                   dish_stats_resource, static_mappings);
  ASSERT_TRUE(response.result.size() == 3);
}
