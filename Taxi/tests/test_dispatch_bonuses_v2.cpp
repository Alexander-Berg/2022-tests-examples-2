#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/dispatch_bonuses/v2/objects.hpp>
#include <ml/dispatch_bonuses/v2/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::dispatch_bonuses::v2;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("dispatch_bonuses_v2");

Params CreateParams() {
  Params params;
  params.scale = 1;
  params.shift = 1;
  params.min_value = -100;
  params.max_value = 100;
  return params;
}

}  // namespace

TEST(DispatchBonusesV2, predictor) {
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, CreateParams());
  ASSERT_EQ(response.predictions.size(), 1ul);
  ASSERT_FLOAT_EQ(response.predictions.front(), 1);
}

TEST(DispatchBonusesV2, predictor_bulk) {
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Resource resource(kTestDataDir + "/resource", true);
  std::vector<Request> requests{request, request, request};
  const auto responses =
      resource.GetPredictor()->ApplyBulk(requests, CreateParams());
  ASSERT_EQ(responses.size(), 3ul);
}
