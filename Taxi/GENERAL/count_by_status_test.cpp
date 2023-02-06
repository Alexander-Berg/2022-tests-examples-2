#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <filters/efficiency/fetch_chain_info/fetch_chain_info.hpp>
#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_driver_status/fetch_driver_status.hpp>
#include "count_by_status.hpp"

using candidates::filters::Context;
using candidates::filters::infrastructure::FetchDriverOrders;
using candidates::filters::infrastructure::FetchDriverStatus;
using candidates::result_storages::CountByStatus;

UTEST(CountByStatusStorage, Sample) {
  CountByStatus storage;
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), CountByStatus::kNoLimit);
  EXPECT_EQ(storage.free(), 0);
  EXPECT_EQ(storage.free_chain(), 0);

  candidates::filters::Context context;
  FetchDriverStatus::Set(context, models::DriverStatus::kOnline);

  storage.Add({}, Context(context));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 1);
  EXPECT_EQ(storage.free(), 1);
  EXPECT_EQ(storage.free_chain(), 0);
  const auto orders = std::make_shared<models::driver_orders::Orders>();
  orders->emplace_back("1", "yandex", models::driver_orders::Status::Driving,
                       std::chrono::system_clock::now());
  FetchDriverOrders::Set(context, orders);
  storage.Add({}, Context(context));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 2);
  EXPECT_EQ(storage.free(), 1);
  EXPECT_EQ(storage.free_chain(), 0);

  candidates::filters::efficiency::FetchChainInfo::Set(
      context, std::make_shared<const models::ChainBusyDriver>());

  storage.Add({}, Context(context));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 3);
  EXPECT_EQ(storage.free(), 1);
  EXPECT_EQ(storage.free_chain(), 1);
}
