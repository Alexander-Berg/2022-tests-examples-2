#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_driver_status/fetch_driver_status.hpp>
#include "status_free.hpp"

using Filter = candidates::filters::infrastructure::StatusFree;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::infrastructure::FetchDriverOrders;
using candidates::filters::infrastructure::FetchDriverStatus;

namespace {
const candidates::filters::FilterInfo kEmptyInfo;
}

TEST(ModernStatusFree, AcceptFreeOnline) {
  Context context;
  candidates::GeoMember member;
  Filter filter(kEmptyInfo);

  FetchDriverStatus::Set(context, models::DriverStatus::kOnline);
  FetchDriverOrders::Set(context, {});
  EXPECT_EQ(filter.Process(member, context), Result::kAllow);
}

TEST(ModernStatusFree, RejectBusyOnline) {
  Context context;
  candidates::GeoMember member;
  Filter filter(kEmptyInfo);

  FetchDriverStatus::Set(context, models::DriverStatus::kOnline);
  const auto orders = std::make_shared<models::driver_orders::Orders>();
  orders->emplace_back("an_order", "any_order_provider",
                       models::driver_orders::Status::Transporting,
                       std::chrono::system_clock::now());
  FetchDriverOrders::Set(context, orders);
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
}

TEST(ModernStatusFree, RejectBusy) {
  Context context;
  candidates::GeoMember member;
  Filter filter(kEmptyInfo);

  FetchDriverStatus::Set(context, models::DriverStatus::kBusy);
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
}

TEST(ModernStatusFree, RejectOffline) {
  Context context;
  candidates::GeoMember member;
  Filter filter(kEmptyInfo);

  FetchDriverStatus::Set(context, models::DriverStatus::kOffline);
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
}
