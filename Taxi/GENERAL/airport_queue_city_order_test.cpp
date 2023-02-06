#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_driver/models/driver.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/utest/utest.hpp>
#include "airport_queue_city_order.hpp"

namespace {
namespace cf = candidates::filters;
namespace cfe = cf::efficiency;
namespace cfi = cf::infrastructure;
namespace cda = clients::dispatch_airport;
namespace drivers_get = cda::v1_active_drivers_queues::get;

const cf::FilterInfo kEmptyInfo;
const std::string kDriverId = "driver_id";

const dispatch_airport_queues_cache::airport_queues_model::TariffClasses
    kTariffClasses{};

const std::vector<std::string> kDispatchClassesOrder{};
const std::string kEkbMainZone = "ekb_airport";
const std::string kVkoMainZone = "vko_airport";
const std::chrono::seconds kFilteredDriversTtl{10};

std::shared_ptr<cfe::AirportQueueCityOrder::AirportQueue> CreateCache(
    bool mix_city_orders) {
  cda::ActiveDriversQueues queues;
  std::vector<cda::ActiveDriver> drivers;
  cda::ActiveDriver driver{kDriverId, std::chrono::system_clock::now()};
  drivers.emplace_back(std::move(driver));
  clients::dispatch_airport::ActiveDriversQueue ekb_queue{"econom",
                                                          std::move(drivers)};
  queues.queues.emplace_back(ekb_queue);

  auto cache = std::make_shared<cfe::AirportQueueCityOrder::AirportQueue>(
      cfe::AirportQueueCityOrder::AirportQueue(kTariffClasses,
                                               kDispatchClassesOrder));
  cache->Update(kEkbMainZone, false, mix_city_orders, {}, kFilteredDriversTtl,
                drivers_get::Response200(queues));
  return cache;
}

class AirportQueueCityOrderTest : public ::testing::Test {
 protected:
  const candidates::GeoMember member{{}, kDriverId};
  cf::Context context{};
};
}  // namespace

TEST_F(AirportQueueCityOrderTest, EmptyCacheCityOrder) {
  const auto empty_cache =
      std::make_shared<cfe::AirportQueueCityOrder::AirportQueue>(
          kTariffClasses, kDispatchClassesOrder);
  const cfe::AirportQueueCityOrder filter(kEmptyInfo, empty_cache, std::nullopt,
                                          {});
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

TEST_F(AirportQueueCityOrderTest, EmptyCacheAirportOrder) {
  const auto empty_cache =
      std::make_shared<cfe::AirportQueueCityOrder::AirportQueue>(
          kTariffClasses, kDispatchClassesOrder);
  const cfe::AirportQueueCityOrder filter(kEmptyInfo, empty_cache, kEkbMainZone,
                                          {});
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

TEST_F(AirportQueueCityOrderTest, CityOrderMixOrdersForbidden) {
  const auto filled_cache = CreateCache(false);
  const cfe::AirportQueueCityOrder filter(kEmptyInfo, filled_cache,
                                          std::nullopt, {});
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}

TEST_F(AirportQueueCityOrderTest, AirportOrderMixOrdersForbidden) {
  const auto filled_cache = CreateCache(false);
  const cfe::AirportQueueCityOrder filter(kEmptyInfo, filled_cache,
                                          kEkbMainZone, {});
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

TEST_F(AirportQueueCityOrderTest, CityOrderMixOrdersAllowed) {
  const auto filled_cache = CreateCache(true);
  const cfe::AirportQueueCityOrder filter(kEmptyInfo, filled_cache,
                                          std::nullopt, {});
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

TEST_F(AirportQueueCityOrderTest, AirportOrderMixOrdersAllowed) {
  const auto filled_cache = CreateCache(true);
  const cfe::AirportQueueCityOrder filter(kEmptyInfo, filled_cache,
                                          kEkbMainZone, {});
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}

TEST_F(AirportQueueCityOrderTest, AnotherAirportOrder) {
  const std::string another_airport_main_zone = "another_airport_main_zone";
  for (const bool mix_city_allowed : {false, true}) {
    const auto filled_cache = CreateCache(mix_city_allowed);
    const cfe::AirportQueueCityOrder filter(kEmptyInfo, filled_cache,
                                            another_airport_main_zone, {});
    EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
  }
}

TEST_F(AirportQueueCityOrderTest, FallbackSearchAirports) {
  const auto filled_cache = CreateCache(false);
  const cfe::AirportQueueCityOrder filterWithoutMainZoneInfo(
      kEmptyInfo, filled_cache, kVkoMainZone, {});
  EXPECT_EQ(filterWithoutMainZoneInfo.Process(member, context),
            cf::Result::kDisallow);

  const cfe::AirportQueueCityOrder filterWithMainZoneInfo(
      kEmptyInfo, filled_cache, kVkoMainZone, {kEkbMainZone});
  filled_cache->Update(kVkoMainZone, false, false, {kEkbMainZone},
                       kFilteredDriversTtl, {});
  EXPECT_EQ(filterWithMainZoneInfo.Process(member, context),
            cf::Result::kAllow);
}
