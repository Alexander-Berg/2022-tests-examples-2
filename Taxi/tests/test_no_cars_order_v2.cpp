#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/common/math_utils.hpp>
#include <ml/no_cars_order/v1/objects.hpp>
#include <ml/no_cars_order/v2/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::no_cars_order::v2;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("no_cars_order_v");
}  // namespace

TEST(NoCarsOrderV2, default_resource) {
  auto request =
      ml::common::FromJsonString<ml::no_cars_order::v1::objects::Request>(
          ml::common::ReadFileContents(kTestDataDir + "1/request.json"));
  ml::no_cars_order::v2::Params params{};
  Resource resource(kTestDataDir + "2/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
  for (const auto& items : response.response_items) {
    ASSERT_EQ(items.raw_value, ml::common::Sigmoid(0.0));
  }
}

TEST(NoCarsOrderV2, constant_resource) {
  auto request =
      ml::common::FromJsonString<ml::no_cars_order::v1::objects::Request>(
          ml::common::ReadFileContents(kTestDataDir + "1/request.json"));
  ml::no_cars_order::v2::Params params{};
  Resource resource(kTestDataDir + "2/resource_constant", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
  for (const auto& items : response.response_items) {
    ASSERT_EQ(items.raw_value, ml::common::Sigmoid(0.0));
    ASSERT_EQ(items.prediction_scale, 1.0);
  }
}

TEST(NoCarsOrderV2, quantile_resource) {
  auto request =
      ml::common::FromJsonString<ml::no_cars_order::v1::objects::Request>(
          ml::common::ReadFileContents(kTestDataDir + "1/request.json"));
  ml::no_cars_order::v2::Params params{};
  for (const auto& elem : request.classes_info) {
    params.quantile_map.emplace(elem.first, 1.0);
  }
  Resource resource(kTestDataDir + "2/resource_quantile", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
  for (const auto& items : response.response_items) {
    ASSERT_EQ(items.raw_value, ml::common::Sigmoid(0.0));
    ASSERT_EQ(items.prediction_scale, 1.0);
  }
}
