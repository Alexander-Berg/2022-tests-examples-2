#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_driver_status/fetch_driver_status.hpp>
#include "status.hpp"

using Filter = candidates::filters::infrastructure::Status;
using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::infrastructure::FetchDriverOrders;
using candidates::filters::infrastructure::FetchDriverStatus;

namespace {
const candidates::filters::FilterInfo kEmptyInfo;
const std::vector<models::DriverStatus> kAnyStatus = {
    models::DriverStatus::kOnline, models::DriverStatus::kBusy,
    models::DriverStatus::kOffline};

}  // namespace

namespace candidates::filters {
inline void PrintTo(Result value, std::ostream* out) {
  switch (value) {
    case Result::kAllow:
      *out << "\"Allow\"";
      break;
    case Result::kDisallow:
      *out << "\"Disallow\"";
      break;
    default:
      *out << "<Unexpected value of " << static_cast<int>(value) << ">";
  }
}
}  // namespace candidates::filters

TEST(Status, NoStatus) {
  Filter::Params params;
  params.only_free = true;
  Filter filter(kEmptyInfo, params);
  Context context;
  GeoMember member;
  EXPECT_ANY_THROW(filter.Process(member, context));
}

TEST(Status, NoneParams) {
  Filter::Params params;
  Filter filter(kEmptyInfo, params);
  Context context;
  GeoMember member;

  for (const auto status : kAnyStatus) {
    FetchDriverStatus::Set(context, status);
    EXPECT_EQ(filter.Process(member, context), Result::kAllow)
        << "Test failed for status " << models::ToString(status);
  }
}

UTEST(Status, OnOrder) {
  Filter::Params params;
  params.on_order = true;
  Filter filter(kEmptyInfo, params);

  Context context;
  GeoMember member;

  for (const auto status : kAnyStatus) {
    FetchDriverStatus::Set(context, status);
    EXPECT_EQ(filter.Process(member, context), Result::kDisallow)
        << "Test failed for status " << models::ToString(status);
  }

  const auto orders = std::make_shared<models::driver_orders::Orders>();
  orders->emplace_back("an_order", "any_order_provider",
                       models::driver_orders::Status::Transporting,
                       std::chrono::system_clock::now());
  FetchDriverOrders::Set(context, orders);
  for (const auto status : kAnyStatus) {
    FetchDriverStatus::Set(context, status);
    EXPECT_EQ(filter.Process(member, context), Result::kAllow)
        << "Test failed for status " << models::ToString(status);
  }
}

TEST(Status, OnlyFree) {
  Filter::Params params;
  params.only_free = true;

  Filter filter(kEmptyInfo, params);

  Context context;
  GeoMember member;

  for (const auto status : kAnyStatus) {
    FetchDriverStatus::Set(context, status);
    Result expected = status == models::DriverStatus::kOnline
                          ? Result::kAllow
                          : Result::kDisallow;
    EXPECT_EQ(filter.Process(member, context), expected)
        << "Test failed for status " << models::ToString(status)
        << ", expected result was "
        << (expected == Result::kAllow ? "kAllow" : "kDisallow");
  }
  const auto orders = std::make_shared<models::driver_orders::Orders>();
  orders->emplace_back("an_order", "any_order_provider",
                       models::driver_orders::Status::Transporting,
                       std::chrono::system_clock::now());
  FetchDriverOrders::Set(context, orders);
  for (const auto status : kAnyStatus) {
    FetchDriverStatus::Set(context, status);
    EXPECT_EQ(filter.Process(member, context), Result::kDisallow)
        << "Test failed for status " << models::ToString(status);
  }
}
