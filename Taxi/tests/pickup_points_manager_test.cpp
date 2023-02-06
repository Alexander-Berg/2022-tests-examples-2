#include <gtest/gtest.h>

#include <clients/pickup-points-manager/client.hpp>
#include <userver/utest/utest.hpp>

namespace test::pickup_points_manager {

using clients::pickup_points_manager::v1_points::get::Parse;
using clients::pickup_points_manager::v1_points::get::PointTags;

TEST(TestPPManager, Tags) {
  ASSERT_EQ(Parse("poi", formats::parse::To<PointTags>()), PointTags::kPoi);
  ASSERT_EQ(Parse("pickup", formats::parse::To<PointTags>()),
            PointTags::kPickup);
  ASSERT_THROW(Parse("kek", formats::parse::To<PointTags>()),
               std::runtime_error);
}

}  // namespace test::pickup_points_manager
