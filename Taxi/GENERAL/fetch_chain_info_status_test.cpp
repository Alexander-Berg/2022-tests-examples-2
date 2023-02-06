#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_driver_status/fetch_driver_status.hpp>
#include "fetch_chain_info.hpp"

using Filter = candidates::filters::efficiency::FetchChainInfo;
using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::infrastructure::FetchDriverOrders;
using candidates::filters::infrastructure::FetchDriverStatus;

namespace {
struct TestContext {
 public:
  explicit TestContext(models::DriverStatus status)
      : chain_busy_drivers_(std::make_shared<models::ChainBusyDrivers>()),
        member_{{}, "dbid_uuid"} {
    FetchDriverStatus::Set(ctx_, status);
    Filter::SetMode(ctx_, Filter::Mode::kChain);

    chain_busy_drivers_->emplace(
        "dbid_uuid", std::make_shared<const models::ChainBusyDriver>());
  }

  Filter CreateFilter() {
    return Filter(kEmptyInfo, zone_class_, chain_busy_drivers_,
                  ::utils::SharedReadablePtr<::models::ComboFree>(nullptr));
  }

  void AddOrder(models::driver_orders::Status status,
                const std::string& provider) {
    static int order_id = 1;
    const auto orders = std::make_shared<models::driver_orders::Orders>();
    orders->emplace_back(std::to_string(order_id++), provider, status,
                         std::chrono::system_clock::now());
    FetchDriverOrders::Set(ctx_, orders);
  }

  void AddOrders(
      const std::initializer_list<
          std::pair<models::driver_orders::Status, std::string>>& orders_skel) {
    static int order_id = 1;
    const auto orders = std::make_shared<models::driver_orders::Orders>();
    std::transform(orders_skel.begin(), orders_skel.end(),
                   std::back_inserter(*orders),
                   [](const auto& item) -> models::driver_orders::Order {
                     return {std::to_string(order_id++), item.second,
                             item.first, std::chrono::system_clock::now()};
                   });
    FetchDriverOrders::Set(ctx_, orders);
  }

  Result Run(const Filter& filter) { return filter.Process(member_, ctx_); }

  Result Run() { return Run(CreateFilter()); }

 private:
  Context ctx_;
  std::shared_ptr<models::ChainBusyDrivers> chain_busy_drivers_;
  GeoMember member_;
  candidates::models::ChainSettings zone_class_;
  const candidates::filters::FilterInfo kEmptyInfo;
};

}  // namespace

UTEST(ModernFetchChainInfo, DontChainBusy) {
  TestContext tc(models::DriverStatus::kBusy);
  EXPECT_EQ(Result::kDisallow, tc.Run());
}

UTEST(ModernFetchChainInfo, DontChainOffline) {
  TestContext tc(models::DriverStatus::kOffline);
  EXPECT_EQ(Result::kDisallow, tc.Run());
}

UTEST(ModernFetchChainInfo, NoThrowOnMissingOrders) {
  TestContext tc(models::DriverStatus::kOnline);
  EXPECT_NO_THROW(tc.Run());
}

UTEST(ModernFetchChainInfo, DontChainWithoutOrders) {
  TestContext tc(models::DriverStatus::kOnline);
  EXPECT_EQ(Result::kDisallow, tc.Run());
}

UTEST(ModernFetchChainInfo, DontChainOnMultipleOrders) {
  using models::driver_orders::Status;
  TestContext tc(models::DriverStatus::kOnline);
  tc.AddOrders(
      {{Status::Driving, "yandex"}, {Status::Transporting, "whatever"}});
  EXPECT_EQ(Result::kDisallow, tc.Run());
}

UTEST(ModernFetchChainInfo, AcceptYandex) {
  TestContext tc(models::DriverStatus::kOnline);
  tc.AddOrder(models::driver_orders::Status::Driving, "yandex");
  EXPECT_EQ(Result::kAllow, tc.Run());
}

UTEST(ModernFetchChainInfo, DontChainNonYandex) {
  TestContext tc(models::DriverStatus::kOnline);
  tc.AddOrder(models::driver_orders::Status::Driving, "not-yandex");
  EXPECT_EQ(Result::kDisallow, tc.Run());
}
