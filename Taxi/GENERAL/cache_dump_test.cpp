#include <geometry/cache_dump.hpp>

#include <limits>

#include <gtest/gtest.h>

#include <userver/dump/common.hpp>
#include <userver/dump/common_containers.hpp>
#include <userver/dump/test_helpers.hpp>

#include <geometry/bounding_box.hpp>
#include <geometry/cartesian_position.hpp>
#include <geometry/line.hpp>
#include <geometry/position.hpp>
#include <geometry/viewport.hpp>

using namespace geometry;

using dump::TestWriteReadCycle;

static_assert(dump::kIsDumpable<Position>);
static_assert(dump::kIsDumpable<PositionDelta>);
static_assert(dump::kIsDumpable<CartesianPosition>);
static_assert(dump::kIsDumpable<BoundingBox>);
static_assert(dump::kIsDumpable<Viewport>);
static_assert(dump::kIsDumpable<CartesianViewport>);
static_assert(dump::kIsDumpable<Line>);

TEST(CacheDump, Position) {
  TestWriteReadCycle(Position{});
  TestWriteReadCycle(Position{10 * lat, 10 * lon});
  TestWriteReadCycle(Position{-500 * lat, 11319 * lon});
  TestWriteReadCycle(Position{std::numeric_limits<double>::infinity() * lat,
                              std::numeric_limits<double>::infinity() * lon});
}

TEST(CacheDump, CartesianPosition) {
  TestWriteReadCycle(CartesianPosition{});
  TestWriteReadCycle(CartesianPosition{55.1 * lat, 30.00001 * lon});
}

TEST(CacheDump, PositionDelta) {
  TestWriteReadCycle(PositionDelta{});
  TestWriteReadCycle(PositionDelta{-0.001 * dlat, 10000 * dlon});
  TestWriteReadCycle(
      PositionDelta{std::numeric_limits<double>::infinity() * dlat,
                    std::numeric_limits<double>::infinity() * dlon});
}

TEST(CacheDump, BoundingBox) {
  TestWriteReadCycle(BoundingBox{});
  TestWriteReadCycle(
      BoundingBox{Position{10 * lon, -11 * lat},
                  Position{
                      std::numeric_limits<double>::infinity() * lat,
                      0.000001 * lon,
                  }});
}

TEST(CacheDump, Viewport) {
  TestWriteReadCycle(Viewport{});
  TestWriteReadCycle(CartesianViewport{});
  TestWriteReadCycle(Viewport{Position{20 * lon, -20 * lat},
                              Position{10 * lon, -10 * lat},
                              /*normalize=*/false});
}

TEST(CacheDump, Line) {
  TestWriteReadCycle(Line{});
  TestWriteReadCycle(Line{Position{10 * lon, -11 * lat},
                          Position{
                              std::numeric_limits<double>::infinity() * lat,
                              0.000001 * lon,
                          }});
}
