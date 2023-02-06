#include "two_circles_batch_generator.hpp"

#include <memory>

#include <gtest/gtest.h>

#include <infraver-geometry/point_serialization.hpp>
#include <models/united_dispatch/segment.hpp>

using united_dispatch::models::Segment;
using SegmentPtr = std::shared_ptr<united_dispatch::models::Segment>;
using ConstSegmentPtr = std::shared_ptr<const united_dispatch::models::Segment>;

TEST(TwoCirclesGeneratorTest, LeaveOnlyNearestSegments) {
  using united_dispatch::waybill::delivery::route_generator::
      LeaveOnlyNearestSegments;
  std::vector<SegmentPtr> segments;

  for (int i = 0; i < 10; ++i) {
    segments.push_back(std::make_shared<Segment>());
    segments.back()->points.push_back({});
    segments.back()->points.front().type = handlers::SegmentPointType::kPickup;
    segments.back()->points.front().coordinates =
        infraver_geometry::Point(30, 30);
  }
  segments.back()->points.front().coordinates =
      infraver_geometry::Point(10, 10);
  std::vector<ConstSegmentPtr> const_segments;
  for (const auto& segment : segments) {
    const_segments.emplace_back(std::move(segment));
  }
  LeaveOnlyNearestSegments(const_segments.back()->points.front().coordinates,
                           const_segments, handlers::SegmentPointType::kPickup,
                           1);
  ASSERT_EQ(const_segments.size(), 1);
}
