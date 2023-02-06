#include <gtest/gtest.h>

#include "iostream"

#include <ml/common/catboost.hpp>
#include <ml/common/filesystem.hpp>
#include <ml/eats/places_ranking/api/v2.hpp>
#include <ml/eats/places_ranking/common/candidates_extractors.hpp>
#include <ml/eats/places_ranking/common/features_extractors/v1.hpp>
#include <ml/eats/places_ranking/common/post_processors.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("eats_places_ranking_api_v2");
}  // namespace

TEST(EatsPlacesRankingCommon, create_objects) {
  using ml::eats::places_ranking::api::v2::Request;
  using namespace ml::eats::places_ranking::common;

  auto features_extractor =
      std::make_shared<FeaturesExtractorV1<Request>>(0, 0, 0, 0, 0);
  auto candidates_extractor =
      std::make_shared<CombinationCandidatesExtractor<Request>>(true, 20, true,
                                                                5);
  auto predictions_extractor =
      std::make_shared<ml::common::CatboostModelMock>(85, 0);
  auto post_processor = std::make_shared<DefaultPostProcessor<Request>>();
  auto personal_rec_model = std::make_shared<RecModelV1<Request>>(
      features_extractor, candidates_extractor, predictions_extractor,
      post_processor);
  auto places_ranker =
      std::make_shared<HeuristicSimpleRanker<Request>>(0, 0, 0);
  auto personal_rec_model_params = RecModelParamsFromJsonString(
      "{\"personal_block_size\": 4, \"personal_rec_model_name\": "
      "\"cxx_v1_rec_model\"}");
  auto catalog_builder = std::make_shared<CatalogBuilder<Request>>(
      personal_rec_model, personal_rec_model_params, places_ranker, "test");
  auto request = ml::eats::places_ranking::objects::v2::RequestFromJsonString(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  std::unordered_map<std::string, double> time_storage;
  catalog_builder->Apply(request, &time_storage);

  // check catboost places go to the top
  auto linear_ranker = std::make_shared<LinearSortRanker<Request>>(
      LinearModelParams{true, 100, 1, 10, 1, 1});
  catalog_builder = std::make_shared<CatalogBuilder<Request>>(
      personal_rec_model, personal_rec_model_params, linear_ranker, "test");
  catalog_builder->Apply(request, &time_storage);
  linear_ranker = std::make_shared<LinearSortRanker<Request>>(LinearModelParams{
      true, -0.068, 0.29, 0, 0.34, 0, 0,           0, 0, 0, 0, 1, 0, 0, 0, 1,
      0,    0,      0,    0, 0,    0, 10000000000, 1, 0, 0, 0, 0, 1, 1, 1, 1});
  catalog_builder = std::make_shared<CatalogBuilder<Request>>(
      personal_rec_model, personal_rec_model_params, linear_ranker, "test");
  auto result_catboost_to_top = catalog_builder->Apply(request, &time_storage);
  for (size_t index = 0; index < 4; ++index) {
    ASSERT_EQ(result_catboost_to_top.result[index].type, "personal");
    std::cout << result_catboost_to_top.result[index].id << std::endl;
  }
  for (size_t index = 4; index < result_catboost_to_top.result.size();
       ++index) {
    ASSERT_EQ(result_catboost_to_top.result[index].type, "ranking");
    std::cout << result_catboost_to_top.result[index].id << std::endl;
  }
  ASSERT_EQ(result_catboost_to_top.result[0].id,
            43750);  // personal place with smallest ETA
  ASSERT_EQ(result_catboost_to_top.result[3].id,
            54401);  // personal place with highest ETA
  ASSERT_EQ(result_catboost_to_top.result[4].id,
            48717);  // ranker place with smallest ETA
  ASSERT_EQ(result_catboost_to_top.result[9].id,
            18071);  // ranker place with highest ETA

  // check catboost places go to bottom
  linear_ranker = std::make_shared<LinearSortRanker<Request>>(LinearModelParams{
      true,
      -0.068,
      0.29,
      0,
      0.34,
      0,
      0,
      0,
      0,
      0,
      0,
      1,
      0,
      0,
      0,
      1,
      0,
      0,
      0,
      0,
      0,
      0,
      -10000000000,
      1,
      1,
      1,
      1,
      1,
      1,
      1,
      1,
      1,
      1,
      1,
      1,
      1,
      1,
      -0.05,
  });

  catalog_builder = std::make_shared<CatalogBuilder<Request>>(
      personal_rec_model, personal_rec_model_params, linear_ranker, "test");
  auto result_catboost_to_bottom =
      catalog_builder->Apply(request, &time_storage);
  for (size_t index = 0; index < 6; ++index) {
    ASSERT_EQ(result_catboost_to_bottom.result[index].type, "ranking");
    std::cout << result_catboost_to_bottom.result[index].id << std::endl;
  }
  for (size_t index = 6; index < result_catboost_to_bottom.result.size();
       ++index) {
    ASSERT_EQ(result_catboost_to_bottom.result[index].type, "personal");
    std::cout << result_catboost_to_bottom.result[index].id << std::endl;
  }
}
