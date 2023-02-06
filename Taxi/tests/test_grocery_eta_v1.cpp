#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/grocery/eta/resources/v1/model.hpp>
#include <ml/grocery/eta/views/v1/predictor.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("grocery_eta_v1");
}  // namespace

TEST(GroceryEtaObectsV1, MLRequest_unpacking) {
  auto request =
      ml::common::FromJsonString<ml::grocery::eta::views::v1::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir + "/request.json"));

  ASSERT_EQ(request,
            ml::common::FromJsonString<ml::grocery::eta::views::v1::MLRequest>(
                ml::common::ToJsonString(request)));

  ASSERT_EQ(request.place_info.place_id, 205743);
}

TEST(GroceryEtaFeatureExtractorV1, feature_extractor) {
  auto request =
      ml::common::FromJsonString<ml::grocery::eta::views::v1::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  auto feature_extractor =
      ml::grocery::eta::views::v1::LoadFeatureExtractorFromDir(
          kTestDataDir + "/model", kTestDataDir + "/static");

  auto features = feature_extractor.Apply(request);
  auto categorical = features.categorical;
  auto numerical = features.numerical;

  ASSERT_EQ(categorical.size(), 14ul);
  ASSERT_EQ(numerical.size(), 334ul);
}

TEST(GroceryEtaPredictor, predictor) {
  auto request =
      ml::common::FromJsonString<ml::grocery::eta::views::v1::MLRequest>(
          ml::common::ReadFileContents(kTestDataDir + "/request.json"));

  bool mock_mode = true;
  ml::grocery::eta::views::v1::PredictorParams default_predictor_params{};
  auto predictor =
      ml::grocery::eta::resources::v1::CreatePredictor(kTestDataDir, mock_mode);
  ASSERT_NO_THROW(predictor->Apply(request, default_predictor_params));

  auto intervalParams =
      ml::grocery::eta::views::v1::PredictorParamsInterval{15, 50, 10};
  default_predictor_params.interval = intervalParams;
  ASSERT_NO_THROW(predictor->Apply(request, default_predictor_params));
  auto response = predictor->Apply(request, default_predictor_params);
  ASSERT_TRUE(response.boundaries.min >= 15 && response.boundaries.max <= 50);
}
