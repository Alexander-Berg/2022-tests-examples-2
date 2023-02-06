#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_driver_status/fetch_driver_status.hpp>
#include "status_active.hpp"

using Filter = candidates::filters::infrastructure::StatusActive;

using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::infrastructure::FetchDriverStatus;

namespace {
const candidates::filters::FilterInfo kEmptyInfo;
}

TEST(StatusMode, RejectNonOnline) {
  Context context;
  GeoMember member;
  Filter filter(kEmptyInfo);

  FetchDriverStatus::Set(context, models::DriverStatus::kBusy);
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);

  FetchDriverStatus::Set(context, models::DriverStatus::kOffline);
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
}

TEST(StatusMode, CheckActive) {
  Context context;
  GeoMember member;
  Filter filter(kEmptyInfo);

  FetchDriverStatus::Set(context, models::DriverStatus::kOnline);
  EXPECT_EQ(filter.Process(member, context), Result::kAllow);

  FetchDriverStatus::Set(context, models::DriverStatus::kBusy);
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);

  FetchDriverStatus::Set(context, models::DriverStatus::kOffline);
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
}

TEST(StatusMode, AcceptFreeOnline) {
  Context context;
  GeoMember member;
  Filter filter(kEmptyInfo);

  FetchDriverStatus::Set(context, models::DriverStatus::kOnline);
  EXPECT_EQ(filter.Process(member, context), Result::kAllow);
}
