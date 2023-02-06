#include <gtest/gtest.h>

#include <fstream>

#include <parsers/driver_eta.hpp>

namespace {

const std::string kDirName = std::string(SOURCE_DIR) + "/tests/static/";

std::string ReadFile(const std::string& filename) {
  std::ifstream file(kDirName + filename);
  return std::string{std::istreambuf_iterator<char>(file),
                     std::istreambuf_iterator<char>()};
}

}  // namespace

TEST(TestDriverEtaV2, TestParsers) {
  const auto& response = ReadFile("eta_v2_response.json");
  models::driver_eta::EtaV2ByClasses eta_v2_by_classes{};
  ASSERT_NO_THROW(eta_v2_by_classes =
                      parsers::driver_eta::ParseEtaV2ByClasses(response));
  ASSERT_EQ(eta_v2_by_classes.count("econom"), 1);
  ASSERT_EQ(eta_v2_by_classes.size(), 1);
  const auto& eta_v2_info = eta_v2_by_classes.at("econom");

  ASSERT_FALSE(eta_v2_info.no_data.value_or(false));
  ASSERT_EQ(eta_v2_info.estimated_time, 83);
  ASSERT_EQ(eta_v2_info.estimated_distance, 262);

  ASSERT_EQ(eta_v2_info.paid_supply_enabled, false);
  ASSERT_EQ(eta_v2_info.no_cars_order_enabled, false);
  ASSERT_EQ(eta_v2_info.order_allowed, true);

  ASSERT_TRUE(eta_v2_info.candidates.has_value());
  ASSERT_EQ(eta_v2_info.candidates->size(), 1);
  const auto& candidate = eta_v2_info.candidates->front();

  ASSERT_EQ(candidate.dbid, "c029875376b84c9e95c86a887df4e895");
  ASSERT_EQ(candidate.uuid, "1e770b4a443325e90678b00c89e5c58a");
  ASSERT_EQ(candidate.position, utils::GeoPoint{56.006677, 54.697759});
  ASSERT_EQ(candidate.status, "free");
  ASSERT_EQ(candidate.route_info.time, 83);
  ASSERT_EQ(candidate.route_info.distance, 262);
  ASSERT_FALSE(candidate.route_info.approximate);
}
