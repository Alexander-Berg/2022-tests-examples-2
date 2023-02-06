#include <gtest/gtest.h>

#include <defs/all_definitions.hpp>
#include <geometry/bounding_box.hpp>
#include "utils/geometry_helpers.hpp"

using geometry::lat;
using geometry::lon;

TEST(TestGeometryHelpers, Increase) {
  {
    geometry::BoundingBox bbox =
        geometry::BoundingBox::FromGeojsonArray({170, 55.0, 174, 57.0});
    ASSERT_TRUE(geometry::AreCloseBoundingBoxes(
        layers::utils::GetIncreasedBbox(bbox, {0.0, 0.0, 0.0, 0.0}), bbox));

    ASSERT_TRUE(geometry::AreCloseBoundingBoxes(
        layers::utils::GetIncreasedBbox(bbox, {0.5, 0.5, 0.5, 0.5}),
        {{168 * lon, 54.0 * lat}, {176 * lon, 58.0 * lat}}));
  }
  {
    geometry::BoundingBox bbox =
        geometry::BoundingBox::FromGeojsonArray({170, 55.0, -160, 57.0});
    ASSERT_TRUE(geometry::AreCloseBoundingBoxes(
        layers::utils::GetIncreasedBbox(bbox, {0.0, 0.0, 0.0, 0.0}), bbox));

    ASSERT_TRUE(geometry::AreCloseBoundingBoxes(
        layers::utils::GetIncreasedBbox(bbox, {0.5, 0.5, 0.5, 0.5}),
        {{155 * lon, 54.0 * lat}, {-145 * lon, 58.0 * lat}}));

    handlers::BboxDelta bbox_delta;
    bbox_delta.west = 0.0;
    bbox_delta.south = 1.0;
    bbox_delta.east = 0.5;
    bbox_delta.north = 2.0;
    ASSERT_TRUE(geometry::AreCloseBoundingBoxes(
        layers::utils::GetIncreasedBbox(bbox, bbox_delta),
        {{170 * lon, 53.0 * lat}, {-145 * lon, 61.0 * lat}}));
  }
}
