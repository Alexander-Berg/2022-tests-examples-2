#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/dispatch_bonuses/v1/objects.hpp>
#include <ml/dispatch_bonuses/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::dispatch_bonuses::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("dispatch_bonuses_v1");
}  // namespace

TEST(DispatchBonusesV1, parse_request) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  ASSERT_EQ(*request.order.id, "e177ff83b85334729d6e1a6630284c13");
  ASSERT_FLOAT_EQ(request.order.source.geopoint.lon, 47.4602989135);
  ASSERT_FLOAT_EQ(request.order.source.geopoint.lat, 42.9909671446);
  ASSERT_FLOAT_EQ(*request.order.surge, 1.0);
  ASSERT_EQ(*request.order.nearest_zone, "makhachkala");
  ASSERT_EQ(request.driver.id, "candidate1");
  ASSERT_FLOAT_EQ(*request.driver.route_info->time, 22);
  ASSERT_FLOAT_EQ(*request.driver.route_info->distance, 141);
  const auto& track_position = request.raw_track[0];
  ASSERT_FLOAT_EQ(track_position.geopoint.lon, 47.457015);
  ASSERT_FLOAT_EQ(track_position.geopoint.lat, 43.000289);
  ASSERT_FLOAT_EQ(track_position.timestamp, 1579285059);
  const auto& prolongations = request.prolongations;
  ASSERT_EQ(prolongations.size(), 2ul);
  ASSERT_EQ(*prolongations[0].eta, 400);
  ASSERT_FLOAT_EQ(*prolongations[1].distance, 1000.1);
  ASSERT_EQ(prolongations[0].method, "alpha_raw");
  ASSERT_FLOAT_EQ(prolongations[1].position.lat, 42.9909671446);

  ml::common::ToJsonString<Request>(request);
}

TEST(DispatchBonusesV1, predictor) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  params.shift = 1;
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
  ASSERT_FLOAT_EQ(response.bonuses.at("default"), 1);
}

TEST(DispatchBonusesV1, predictor_bulk) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Resource resource(kTestDataDir + "/resource", true);
  std::vector<Request> requests{request, request, request};
  const auto responses = resource.GetPredictor()->ApplyBulk(requests, {});
  ASSERT_FLOAT_EQ(responses.size(), 3ul);
}
