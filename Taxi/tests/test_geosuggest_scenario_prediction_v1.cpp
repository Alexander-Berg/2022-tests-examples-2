#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/geosuggest/common/objects.hpp>
#include <ml/geosuggest/scenario_prediction/v1/objects.hpp>
#include <ml/geosuggest/scenario_prediction/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::geosuggest::scenario_prediction::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("geosuggest_scenario_prediction_v1");

Resource GetResource(std::string&& dir_name) {
  return Resource(kTestDataDir + "/resource/" + dir_name, true);
}

}  // namespace

TEST(ScenarioPredictionV1, recommender) {
  const auto resource = GetResource("taxi_order");
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto predictor = resource.GetPredictor();
  Params params;

  auto response = predictor->Apply(request, params);
  ASSERT_GT(response.relevance, 0.0);
  ASSERT_LE(response.relevance, 1.0);
}
