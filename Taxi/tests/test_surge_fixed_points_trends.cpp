#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/common/geopoint.hpp>
#include <ml/surge_statistics/surge_fixed_points/trend/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::surge_statistics::surge_fixed_points::trend;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("surge_fixed_points_trend");
}  // namespace

TEST(SurgeFixedPointsTrend, trends_storage_from_json) {
  const Resource resource{kTestDataDir + "/resource", true};
  const auto& storage = resource.GetPointTrendsStorage();
  ASSERT_EQ(storage->trends_storage.size(), 2ul);
}

TEST(SurgeFixedPointsTrend, trends_storage_adding_elements) {
  PointTrendsStorage trends;
  static const std::string GEOPOINT_ID = "3124254";
  trends.AddTimeElem(GEOPOINT_ID, "deviation", "2022-01-10 00:00:00", 23);
  const auto& trends_storage = trends.trends_storage;
  ASSERT_EQ(trends_storage.size(), 1ul);
  ASSERT_EQ(trends_storage.at(GEOPOINT_ID).size(), 1ul);
  ASSERT_EQ(trends_storage.at(GEOPOINT_ID).at("deviation").size(), 1ul);
  ASSERT_EQ(
      trends_storage.at(GEOPOINT_ID).at("deviation").at("2022-01-10 00:00:00"),
      23);
}
