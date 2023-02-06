#include <gtest/gtest.h>

#include <unordered_set>

#include <models/shuttle_positions.hpp>

namespace {

using ShuttleIdT = shuttle_control::models::ShuttleIdT;
using GpsSignal = ::gpssignal::GpsSignal;
using DataT = shuttle_control::models::ShuttlePositions::DataT;
using PositionsDataT = shuttle_control::models::ShuttlePositions::PositionDataT;
using BoundingBox = ::geometry::BoundingBox;
using Position = ::geometry::Position;

Position MakePosition(const double lon, const double lat) {
  return Position{lon * geometry::lon, lat * geometry::lat};
}

GpsSignal MakeGpsSignal(const double lon, const double lat) {
  return GpsSignal{MakePosition(lon, lat)};
}

const BoundingBox kInfiniteBbox{MakePosition(-180.0, -90.0),
                                MakePosition(180.0, 90.0)};

}  // namespace

TEST(ShuttlePositions, Empty) {
  DataT empty{};
  const auto source = shuttle_control::models::PositionSource::kRaw;

  const shuttle_control::models::ShuttlePositions cache{std::move(empty)};

  ASSERT_EQ(cache.GetLastPosition(ShuttleIdT{123}, source), std::nullopt);
  ASSERT_EQ(cache.GetLastShuttlePositionsInArea(kInfiniteBbox, source),
            PositionsDataT{});
}

TEST(ShuttlePositions, Simple) {
  DataT data{
      {ShuttleIdT{123}, {{MakeGpsSignal(50.0, 30.1)}, {}}},
      {ShuttleIdT{124}, {{MakeGpsSignal(51.0, 30.0)}, {}}},
      {ShuttleIdT{125}, {{MakeGpsSignal(48.0, 31.8)}, {}}},
      {ShuttleIdT{126}, {{MakeGpsSignal(51.0, 25.1)}, {}}},
      {ShuttleIdT{127}, {{MakeGpsSignal(50.0, 30.1)}, {}}},
      {ShuttleIdT{130}, {{MakeGpsSignal(50.0, 45.1)}, {}}},
      {ShuttleIdT{131}, {{MakeGpsSignal(-180.0, -90.0)}, {}}},
      {ShuttleIdT{132}, {{MakeGpsSignal(180.0, 90.0)}, {}}},
  };
  const auto source = shuttle_control::models::PositionSource::kRaw;

  const shuttle_control::models::ShuttlePositions cache{std::move(data)};

  ASSERT_EQ(cache.GetLastPosition(ShuttleIdT{122}, source), std::nullopt);
  ASSERT_EQ(cache.GetLastPosition(ShuttleIdT{123}, source),
            MakeGpsSignal(50.0, 30.1));
  ASSERT_EQ(cache.GetLastPosition(ShuttleIdT{124}, source),
            MakeGpsSignal(51.0, 30.0));
  ASSERT_EQ(cache.GetLastPosition(ShuttleIdT{126}, source),
            MakeGpsSignal(51.0, 25.1));
  ASSERT_EQ(cache.GetLastPosition(ShuttleIdT{131}, source),
            MakeGpsSignal(-180.0, -90.0));

  {
    const BoundingBox bbox{MakePosition(15.0, 20.0), MakePosition(45.0, 30.0)};
    ASSERT_EQ(cache.GetLastShuttlePositionsInArea(bbox, source),
              PositionsDataT{});
  }

  {
    const BoundingBox bbox{MakePosition(-180.0, -90.0),
                           MakePosition(-179.9, -89.9)};
    const PositionsDataT expected{
        {ShuttleIdT{131}, MakeGpsSignal(-180.0, -90.0)}};
    ASSERT_EQ(cache.GetLastShuttlePositionsInArea(bbox, source), expected);
  }

  {
    const BoundingBox bbox{MakePosition(49.0, 29.0), MakePosition(52.0, 32.0)};
    const PositionsDataT expected{{ShuttleIdT{123}, MakeGpsSignal(50.0, 30.1)},
                                  {ShuttleIdT{124}, MakeGpsSignal(51.0, 30.0)},
                                  {ShuttleIdT{127}, MakeGpsSignal(50.0, 30.1)}};
    ASSERT_EQ(cache.GetLastShuttlePositionsInArea(bbox, source), expected);
  }

  {
    const PositionsDataT expected{
        {ShuttleIdT{123}, MakeGpsSignal(50.0, 30.1)},
        {ShuttleIdT{124}, MakeGpsSignal(51.0, 30.0)},
        {ShuttleIdT{125}, MakeGpsSignal(48.0, 31.8)},
        {ShuttleIdT{126}, MakeGpsSignal(51.0, 25.1)},
        {ShuttleIdT{127}, MakeGpsSignal(50.0, 30.1)},
        {ShuttleIdT{130}, MakeGpsSignal(50.0, 45.1)},
        {ShuttleIdT{131}, MakeGpsSignal(-180.0, -90.0)},
        {ShuttleIdT{132}, MakeGpsSignal(180.0, 90.0)}};
    ASSERT_EQ(cache.GetLastShuttlePositionsInArea(kInfiniteBbox, source),
              expected);
  }
}
