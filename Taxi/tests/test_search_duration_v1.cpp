#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/search_duration/v1/features_extractor.hpp>
#include <ml/search_duration/v1/objects.hpp>
#include <ml/search_duration/v1/predictor.hpp>
#include <ml/search_duration/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::search_duration::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("search_duration_v1");
}  // namespace

TEST(SearchDurationV1, features_extractor) {
  auto request = ml::common::FromJsonString<ml::search_duration::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto features_config = ml::common::FromJsonString<FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  ASSERT_EQ(features_config.geo_combinations_count, 5);
  const auto features_extractor =
      ml::search_duration::v1::FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
}

TEST(SearchDurationV1, resource) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  Resource resource(kTestDataDir + "/resource", true);
  ASSERT_NO_THROW(resource.GetPredictor()->Apply(request, params));
}
