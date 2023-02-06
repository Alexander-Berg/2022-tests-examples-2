#include <gtest/gtest.h>

#include <filters/infrastructure/mo_permits/mo_permits.hpp>
#include "deptrans.hpp"

using candidates::filters::Context;
using candidates::filters::infrastructure::MOPermits;
using candidates::result_storages::DepTrans;

namespace {

std::vector<models::geometry::Point> MakeSearchArea() {
  return {
      {37.309394, 55.914744}, {37.884803, 55.911659}, {37.942481, 55.520175},
      {37.242102, 55.499913}, {37.309394, 55.914744},
  };
}

}  // namespace

TEST(DepTransStorage, Sample) {
  DepTrans storage(MakeSearchArea());
  EXPECT_EQ(storage.expected_count(), DepTrans::kNoLimit);
  Context context;
  MOPermits::Set(context, models::DeptransPermissionInfo{
                              {{models::kMoscowLicenseIssuer, "val"}}, {}});
  storage.Add({{0, 0}, "id1"}, Context(context));
  storage.Add({{37.585425, 55.745469}, "id2"}, Context(context));
  EXPECT_EQ(storage.size(), 2);
  MOPermits::Set(context,
                 models::DeptransPermissionInfo{
                     {{models::kMoscowRegionLicenseIssuer, "val"}}, {}});
  storage.Add({{0, 0}, "id3"}, Context(context));
  EXPECT_EQ(storage.size(), 2);
  storage.Add({{37.585425, 55.745469}, "id4"}, Context(context));
  EXPECT_EQ(storage.size(), 3);
  EXPECT_EQ(storage.expected_count(), DepTrans::kNoLimit);
}
