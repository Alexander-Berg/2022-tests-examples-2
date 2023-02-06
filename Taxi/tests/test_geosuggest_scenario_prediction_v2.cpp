#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/geosuggest/common/objects.hpp>
#include <ml/geosuggest/scenario_prediction/v2/objects.hpp>
#include <ml/geosuggest/scenario_prediction/v2/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::geosuggest::scenario_prediction::v2;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("geosuggest_scenario_prediction_v2");

Resource GetResource(std::string&& dir_name) {
  return Resource(kTestDataDir + "/resource/" + dir_name, true);
}

}  // namespace

TEST(ScenarioPredictionV2, recommender) {
  const auto resource = GetResource("promoblocks_summary");
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto predictor = resource.GetPredictor();
  Params params;

  auto response = predictor->Apply(request, params);
  ASSERT_EQ(response.results.size(), 1ul);
  const auto& result = response.results.at(0);
  ASSERT_GT(result.relevance, 0.0);
  ASSERT_LE(result.relevance, 1.0);
  ASSERT_EQ(result.scenario, "econom");
}
