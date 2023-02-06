#include "format_route.hpp"

#include <geometry/position_as_array_serialization.hpp>
#include <userver/formats/json.hpp>

#include <gtest/gtest.h>

TEST(limit_precision, base) {
  const ::geometry::Position p(37.37373712345678 * ::geometry::lon,
                               55.555555123456789 * ::geometry::lat);
  const auto limited = driver_route_watcher::internal::LimitPrecision(p);
  const auto serialized = formats::json::ToString(geometry::Serialize(
      limited, formats::serialize::To<formats::json::Value>{}));
  ASSERT_EQ("[37.373737,55.555555]", serialized);
}
