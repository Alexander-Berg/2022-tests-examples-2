#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <initializer_list>

#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_driver_status/fetch_driver_status.hpp>
#include "status_list.hpp"

using Filter = candidates::filters::infrastructure::StatusList;

using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::infrastructure::FetchDriverOrders;
using candidates::filters::infrastructure::FetchDriverStatus;
using Taximeter = models::LegacyTaximeterStatus;

namespace {

class TestEnv {
 public:
  Result Run(std::vector<Taximeter>&& statuses) {
    const candidates::filters::FilterInfo empty_info;
    Filter filter(empty_info, std::move(statuses));
    if (orders_) FetchDriverOrders::Set(context_, *orders_);
    return filter.Process(member_, context_);
  }

  TestEnv& SetDriverStatus(models::DriverStatus driver_status) {
    FetchDriverStatus::Set(context_, driver_status);
    return *this;
  }

  TestEnv& AddOrder(models::driver_orders::Status order_status) {
    if (!orders_)
      orders_.emplace(std::make_shared<models::driver_orders::Orders>());
    (*orders_)->emplace_back("order_" + std::to_string(++order_id_), "yandex",
                             order_status, std::chrono::system_clock::now());
    return *this;
  }

 private:
  Context context_;
  GeoMember member_;
  std::optional<std::shared_ptr<models::driver_orders::Orders>> orders_;
  int order_id_ = 0;
};

}  // namespace

TEST(StatusList, Free) {
  TestEnv env;
  env.SetDriverStatus(models::DriverStatus::kOnline);

  EXPECT_EQ(env.Run({Taximeter::kFree}), Result::kAllow);
  EXPECT_EQ(env.Run({Taximeter::kBusy, Taximeter::kOrderBusy, Taximeter::kOrder,
                     Taximeter::kOff}),
            Result::kDisallow);
}

TEST(StatusList, Busy) {
  TestEnv env;
  env.SetDriverStatus(models::DriverStatus::kBusy);
  EXPECT_EQ(env.Run({Taximeter::kBusy}), Result::kAllow);
  EXPECT_EQ(env.Run({Taximeter::kFree, Taximeter::kOrder, Taximeter::kOrder,
                     Taximeter::kOrderBusy}),
            Result::kDisallow);
}

UTEST(StatusList, Order) {
  TestEnv env;
  env.SetDriverStatus(models::DriverStatus::kBusy)
      .AddOrder(models::driver_orders::Status::Transporting);
  EXPECT_EQ(env.Run({Taximeter::kOrderBusy}), Result::kAllow);
  EXPECT_EQ(env.Run({Taximeter::kFree, Taximeter::kOrder, Taximeter::kOff}),
            Result::kDisallow);

  env.SetDriverStatus(models::DriverStatus::kOnline);
  EXPECT_EQ(env.Run({Taximeter::kOrder}), Result::kAllow);
  EXPECT_EQ(env.Run({Taximeter::kFree, Taximeter::kOrderBusy, Taximeter::kOff}),
            Result::kDisallow);
}
