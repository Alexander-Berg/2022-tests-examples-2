#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/geosuggest/clarify_points/shared/objects.hpp>
#include <ml/geosuggest/clarify_points/v1/generated/objects.hpp>
#include <ml/geosuggest/clarify_points/v1/model/features_extractor.hpp>
#include <ml/geosuggest/clarify_points/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::geosuggest::clarify_points::v1;
using Request = ml::geosuggest::clarify_points::shared::Request;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("geosuggest_clarify_points_v1");

Resource GetResource(const std::string& dir_name) {
  return Resource(kTestDataDir + "/resource/" + dir_name, true);
}

generated::PredictorConfig GetConfig(const std::string& resource_dir) {
  auto config = ml::common::FromJsonString<generated::PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/" + resource_dir +
                                   "/config.json"));
  return config;

}  // namespace
TEST(ClarifyPointsV1, recommender) {
  std::vector<std::string> resource_dirs{"clarify_points",
                                         "clarify_points_old_compatibility"};
  std::vector<std::size_t> cat_features_num{31, 13};
  std::vector<std::size_t> numerical_features_num{242, 38};
  for (size_t i = 0; i < resource_dirs.size(); i++) {
    const auto& resource_dir = resource_dirs.at(i);
    const auto config = GetConfig(resource_dir);
    const auto resource = GetResource(resource_dir);
    std::vector<Request> requests{};
    requests.emplace_back(ml::common::FromJsonString<Request>(
        ml::common::ReadFileContents(kTestDataDir + "/request.json")));
    requests.emplace_back(ml::common::FromJsonString<Request>(
        ml::common::ReadFileContents(kTestDataDir + "/request2.json")));
    const auto features_extractor = FeaturesExtractor(config.features_config);
    const auto predictor = resource.GetPredictor();

    for (const auto& request : requests) {
      const auto features = features_extractor.Apply(request);
      ASSERT_EQ(features.categorical.size(), cat_features_num.at(i));
      ASSERT_EQ(features.numerical.size(), numerical_features_num.at(i));
      auto response = predictor->Apply(request);
      ASSERT_EQ(response.shift_probability, 0.5);
      ASSERT_TRUE(!request.orders.empty());
    }
  }
}
}  // namespace
