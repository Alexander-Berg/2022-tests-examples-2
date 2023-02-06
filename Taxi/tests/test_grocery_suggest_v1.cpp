#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/grocery/suggest/resources/v1/model_resource.hpp>
#include <ml/grocery/suggest/resources/v1/ranker/utils.hpp>
#include <ml/grocery/suggest/resources/v1/static_resource.hpp>
#include <ml/grocery/suggest/views/v1/objects.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("grocery_suggest_v1");

const std::string kTestDataWithoutHistoryResourcesDir =
    kTestDataDir + "/without_history/resources/";
const std::string kTestDataWithHistoryResourcesDir =
    kTestDataDir + "/with_history/resources/";
}  // namespace

TEST(GrocerySuggestResources, StaticResource) {
  const auto resource_wrapper =
      ml::grocery::suggest::resources::v1::static_resource::Resource(
          kTestDataWithoutHistoryResourcesDir, false);
  const auto static_resource = resource_wrapper.GetStaticResource();
  const auto item_info =
      static_resource->GetItemInfo("ba8ec170-022a-11ea-b7fe-ac1f6b974fa0");
  EXPECT_EQ(item_info.product_id, "ba8ec170-022a-11ea-b7fe-ac1f6b974fa0");
  const auto items_by_category =
      static_resource->GetItemsByCategory("Просто хлеб");
  ASSERT_TRUE(items_by_category.has_value());
  EXPECT_EQ(items_by_category.value().size(), 2ul);
  const auto pair_info =
      static_resource->GetPairInfo("ba8ec170-022a-11ea-b7fe-ac1f6b974fa0",
                                   "ba8ec180-022a-11ea-b7fe-ac1f6b974fa0");
  ASSERT_TRUE(pair_info.has_value());
  EXPECT_NEAR(pair_info.value().npmi, 0.13515503603605478, 1e-4);
  EXPECT_NEAR(pair_info.value().pmi, 0.405465, 1e-4);
}

TEST(GrocerySuggestResources, ModelResource) {
  const auto static_resource_wrapper =
      ml::grocery::suggest::resources::v1::static_resource::Resource(
          kTestDataWithoutHistoryResourcesDir, false);
  const auto model_resource_wrapper =
      ml::grocery::suggest::resources::v1::model_resource::Resource(
          kTestDataWithoutHistoryResourcesDir, true);
  std::vector<std::string> request_names = {
      "request.json", "request2.json", "request3_no_metadata_candidate.json"};
  // from requests above
  std::unordered_set<std::string> potential_candidate_ids = {
      "ba8ec170-022a-11ea-b7fe-ac1f6b974fa0", "no_metadata_candidate_id"};
  for (const auto& request_name : request_names) {
    const auto request =
        ml::common::FromJsonString<ml::grocery::suggest::views::v1::MLRequest>(
            ml::common::ReadFileContents(kTestDataDir + "/" + request_name));
    const auto ranker = model_resource_wrapper.GetRanker();
    const auto static_resource = static_resource_wrapper.GetStaticResource();
    auto response = ranker->Apply(request, static_resource);
    ASSERT_EQ(response.ranked_items.size(), request.candidates.size());
    ASSERT_TRUE(
        potential_candidate_ids.count(response.ranked_items.at(0).product_id));
    ASSERT_GE(response.ranked_items.at(0).score, 0);
    ASSERT_LE(response.ranked_items.at(0).score, 1);
  }
}

TEST(GrocerySuggestResources, ModelResourceWithHistory) {
  const auto static_resource_wrapper =
      ml::grocery::suggest::resources::v1::static_resource::Resource(
          kTestDataWithHistoryResourcesDir, false);
  const auto model_resource_wrapper =
      ml::grocery::suggest::resources::v1::model_resource::Resource(
          kTestDataWithHistoryResourcesDir, true);
  std::vector<std::string> request_names = {
      "request.json", "request2.json", "request3_no_metadata_candidate.json",
      "user_history_request.json"};
  // from requests above
  for (const auto& request_name : request_names) {
    const auto request =
        ml::common::FromJsonString<ml::grocery::suggest::views::v1::MLRequest>(
            ml::common::ReadFileContents(kTestDataDir + "/" + request_name));
    const auto ranker = model_resource_wrapper.GetRanker();
    const auto static_resource = static_resource_wrapper.GetStaticResource();
    auto response = ranker->Apply(request, static_resource);
    ASSERT_EQ(response.ranked_items.size(), request.candidates.size());
    ASSERT_GE(response.ranked_items.at(0).score, 0);
    ASSERT_LE(response.ranked_items.at(0).score, 1);
  }
}

TEST(GrocerySuggestResources, FeatureExtractorWithHistory) {
  const auto static_resource_wrapper =
      ml::grocery::suggest::resources::v1::static_resource::Resource(
          kTestDataWithHistoryResourcesDir, false);
  const auto static_resource = static_resource_wrapper.GetStaticResource();
  const auto features_config = ml::common::FromJsonString<
      ml::grocery::suggest::views::v1::FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataWithHistoryResourcesDir +
                                   "/config.json"));
  const auto feature_extractor =
      ml::grocery::suggest::resources::v1::ranker::FeaturesExtractor(
          features_config);

  const auto request =
      ml::common::FromJsonString<ml::grocery::suggest::views::v1::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir +
                                       "/user_history_request.json"));
  const auto result = feature_extractor.Apply(request, static_resource);
  auto expected_json_str = ml::common::ReadFileContents(
      kTestDataDir + "/expected_result_user_history.json");
  const auto expected_json = formats::json::FromString(expected_json_str);
  const auto expected_categorical =
      expected_json["categorical"].As<decltype(result.categorical)>();
  const auto expected_numerical =
      expected_json["numerical"].As<std::vector<std::vector<double>>>();
  ASSERT_EQ(expected_categorical.size(), result.categorical.size());
  ASSERT_EQ(expected_categorical.back().size(),
            result.categorical.back().size());
  for (size_t i = 0; i < expected_categorical.size(); i++) {
    for (size_t j = 0; j < expected_categorical[i].size(); j++) {
      ASSERT_EQ(expected_categorical[i][j], result.categorical[i][j]);
    }
  }

  ASSERT_EQ(expected_numerical.size(), result.numerical.size());
  ASSERT_EQ(expected_numerical.back().size(), result.numerical.back().size());
  for (size_t i = 0; i < expected_numerical.size(); i++) {
    for (size_t j = 0; j < expected_numerical[i].size(); j++) {
      if (!(abs(expected_numerical[i][j] - result.numerical[i][j]) < 1e-5)) {
        ASSERT_TRUE(true);
      }
      ASSERT_TRUE(abs(expected_numerical[i][j] - result.numerical[i][j]) <
                  1e-5);
    }
  }
}

TEST(GrocerySuggestResources, FeatureExtractor) {
  const auto static_resource_wrapper =
      ml::grocery::suggest::resources::v1::static_resource::Resource(
          kTestDataWithoutHistoryResourcesDir, false);
  const auto static_resource = static_resource_wrapper.GetStaticResource();
  const auto feature_extractor =
      ml::grocery::suggest::resources::v1::ranker::FeaturesExtractor({});

  const auto request =
      ml::common::FromJsonString<ml::grocery::suggest::views::v1::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir + "/request2.json"));
  const auto result = feature_extractor.Apply(request, static_resource);
  double not_a_number =
      ml::grocery::suggest::resources::v1::ranker::utils::kMissingNumFeature;
  // only 1 candidate is present, so we check only 0 index
  std::vector<std::vector<std::string>> expected_categorical = {
      {"185758cat", "5cat", "2cat", "1cat"}};
  ASSERT_EQ(expected_categorical.size(), result.categorical.size());
  ASSERT_EQ(expected_categorical.back().size(),
            result.categorical.back().size());
  for (size_t i = 0; i < expected_categorical.back().size(); i++) {
    ASSERT_EQ(expected_categorical.back()[i], result.categorical.back()[i]);
  }

  // these are taken from python feature extractor
  // with same resources
  std::vector<std::vector<double>> expected_numerical = {
      {353.000000,   53.000000,    82370.000000, 0.000000,     0.405465,
       0.405465,     0.405465,     0.405465,     0.135155,     0.135155,
       0.135155,     0.135155,     not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       -1.000000,    -1.000000,    -1.000000,    1.000000,     1.000000,
       1.000000,     1.000000,     1.000000,     1.000000,     1.000000,
       1.000000,     1.000000,     1.000000,     not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, 1.000000,     1.000000,     1.000000}};
  // NaNs are from category affinity, embeddings are opposite hence -1's
  // NaNs ranks are also NaN
  ASSERT_EQ(expected_numerical.size(), result.numerical.size());
  ASSERT_EQ(expected_numerical.back().size(), result.numerical.back().size());
  for (size_t i = 0; i < expected_numerical.back().size(); i++) {
    ASSERT_TRUE(abs(expected_numerical.back()[i] - result.numerical.back()[i]) <
                1e-5);
  }
}

TEST(GrocerySuggestResources, FeatureExtractorItemPage) {
  const auto static_resource_wrapper =
      ml::grocery::suggest::resources::v1::static_resource::Resource(
          kTestDataWithoutHistoryResourcesDir, false);
  const auto static_resource = static_resource_wrapper.GetStaticResource();
  const auto feature_extractor =
      ml::grocery::suggest::resources::v1::ranker::FeaturesExtractor({});

  const auto request =
      ml::common::FromJsonString<ml::grocery::suggest::views::v1::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir +
                                       "/request_item_page.json"));
  const auto result = feature_extractor.Apply(request, static_resource);
  double not_a_number =
      ml::grocery::suggest::resources::v1::ranker::utils::kMissingNumFeature;
  // only 1 candidate is present, so we check only 0 index
  std::vector<std::vector<std::string>> expected_categorical = {
      {"185758cat", "5cat", "2cat", "1cat"}};
  ASSERT_EQ(expected_categorical.size(), result.categorical.size());
  ASSERT_EQ(expected_categorical.back().size(),
            result.categorical.back().size());
  for (size_t i = 0; i < expected_categorical.back().size(); i++) {
    ASSERT_EQ(expected_categorical.back()[i], result.categorical.back()[i]);
  }
  std::vector<std::vector<double>> expected_numerical = {
      {353.000000,   53.000000,    82370.000000, 0.000000,     0.405465,
       0.405465,     0.405465,     0.405465,     0.135155,     0.135155,
       0.135155,     0.135155,     not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       -1.000000,    -1.000000,    -1.000000,    1.000000,     1.000000,
       1.000000,     1.000000,     1.000000,     1.000000,     1.000000,
       1.000000,     1.000000,     1.000000,     not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, 1.000000,     1.000000,     1.000000}};
  ASSERT_EQ(expected_numerical.size(), result.numerical.size());
  ASSERT_EQ(expected_numerical.back().size(), result.numerical.back().size());
  for (size_t i = 0; i < expected_numerical.back().size(); i++) {
    ASSERT_TRUE(abs(expected_numerical.back()[i] - result.numerical.back()[i]) <
                1e-5);
  }
}

TEST(GrocerySuggestResources, FeatureExtractorNoMetadata) {
  const auto static_resource_wrapper =
      ml::grocery::suggest::resources::v1::static_resource::Resource(
          kTestDataWithoutHistoryResourcesDir, false);
  const auto static_resource = static_resource_wrapper.GetStaticResource();
  const auto feature_extractor =
      ml::grocery::suggest::resources::v1::ranker::FeaturesExtractor({});

  const auto request =
      ml::common::FromJsonString<ml::grocery::suggest::views::v1::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir +
                                       "/request3_no_metadata_candidate.json"));
  const auto result = feature_extractor.Apply(request, static_resource);
  double not_a_number =
      ml::grocery::suggest::resources::v1::ranker::utils::kMissingNumFeature;
  // only 1 candidate is present, so we check only 0 index
  std::vector<std::vector<std::string>> expected_categorical = {
      {"185758cat", "5cat", "2cat", "1cat"}};
  ASSERT_EQ(expected_categorical.size(), result.categorical.size());
  ASSERT_EQ(expected_categorical.back().size(),
            result.categorical.back().size());
  for (size_t i = 0; i < expected_categorical.back().size(); i++) {
    ASSERT_EQ(expected_categorical.back()[i], result.categorical.back()[i]);
  }

  // no metadatada, so only NaNs + 2 ranks for fake ctr/count
  std::vector<std::vector<double>> expected_numerical = {
      {353.000000,   53.000000,    not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number, not_a_number,
       not_a_number, not_a_number, not_a_number, not_a_number}};
  ASSERT_EQ(expected_numerical.size(), result.numerical.size());
  ASSERT_EQ(expected_numerical.back().size(), result.numerical.back().size());
  for (size_t i = 0; i < expected_numerical.back().size(); i++) {
    ASSERT_TRUE(abs(expected_numerical.back()[i] - result.numerical.back()[i]) <
                1e-5);
  }
}
