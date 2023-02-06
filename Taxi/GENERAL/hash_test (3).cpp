#include <geobus-sharding/hash.hpp>

#include <userver/utest/utest.hpp>

namespace {

using driver_id::DriverDbidUndscrUuid;
using driver_id::DriverDbidView;
using driver_id::DriverUuidView;

TEST(TestHash, TestHashFromViews) {
  ASSERT_EQ(7878445591185401914ull,
            geobus_sharding::Hash(
                DriverDbidView{"812ef461837d45ac8c714f0b9a94d2c9"},
                DriverUuidView{"c5f231580f701eaed75791392e561eb5"}));
}

TEST(TestHash, TestHashFromDbidUndscrUuid) {
  ASSERT_EQ(3096957691686750323ull, geobus_sharding::Hash(DriverDbidUndscrUuid{
                                        "cd7b9e461a60472e86dacb5d08532ccb_"
                                        "77d5623a34bb9c8a3639a0d7e92ca0f2"}));
}

}  // namespace
