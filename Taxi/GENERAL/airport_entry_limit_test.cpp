#include "airport_entry_limit.hpp"

#include <gtest/gtest.h>

#include <userver/dynamic_config/snapshot.hpp>
#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_route_info/fetch_route_info.hpp>

namespace {
namespace cf = candidates::filters;
namespace cfe = cf::efficiency;
namespace cfi = cf::infrastructure;
namespace cda = clients::dispatch_airport;
namespace drivers_get = cda::v1_active_drivers_queues::get;

using cfi::FetchRouteInfo;

const cf::FilterInfo kEmptyInfo;

const std::string kEkbMainZone = "ekb_airport";
const std::string kVkoMainZone = "vko_airport";

auto MakeEntryLimitZone(std::string main_zone, int raw = 0,
                        double percent = 0) {
  return cfe::EntryLimitZone{main_zone, std::chrono::seconds(raw), percent};
}

auto Time(std::time_t t) { return std::chrono::system_clock::from_time_t(t); };

std::shared_ptr<cfe::AirportEntryLimit::AirportQueue> CreateCache() {
  return std::make_shared<cfe::AirportEntryLimit::AirportQueue>(
      cfe::AirportEntryLimit::AirportQueue({}, {}, true, true));
}

void UpdateCache(std::shared_ptr<cfe::AirportEntryLimit::AirportQueue> cache,
                 const std::string& main_zone,
                 std::vector<cda::EntryLimitReachedDriver>&& drivers) {
  cda::ActiveDriversQueues queues;
  queues.entry_limit_reached = std::move(drivers);
  cache->Update(main_zone, false, false, {}, {},
                drivers_get::Response200(queues));
}

class AirportEntryLimitTest : public ::testing::Test {
 protected:
  cf::Context context{};
  const std::chrono::system_clock::time_point now = Time(120);
  void SetFetchRouteInfo(std::chrono::seconds time) {
    models::RouteInfo route_info;
    route_info.time = time;
    FetchRouteInfo::Set(context, route_info);
  }
};

}  // namespace

TEST_F(AirportEntryLimitTest, EmptyCache) {
  const auto empty_cache = CreateCache();
  SetFetchRouteInfo(std::chrono::seconds(120));
  const cfe::AirportEntryLimit filter(kEmptyInfo, empty_cache, now,
                                      MakeEntryLimitZone(kEkbMainZone), {}, {});
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id1"}, context),
            cf::Result::kAllow);
}

TEST_F(AirportEntryLimitTest, SourceInAirport) {
  const auto filled_cache = CreateCache();
  UpdateCache(filled_cache, kVkoMainZone, {{"driver_id4", Time(300)}});
  UpdateCache(filled_cache, kEkbMainZone,
              {
                  {"driver_id2", Time(300)},
                  {"driver_id3", Time(150)},
              });
  SetFetchRouteInfo(std::chrono::seconds(120));
  const cfe::AirportEntryLimit filter(kEmptyInfo, filled_cache, now,
                                      MakeEntryLimitZone(kEkbMainZone), {}, {});
  // Not limited
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id1"}, context),
            cf::Result::kAllow);
  // Limited
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id2"}, context),
            cf::Result::kDisallow);
  // Limit drops before arrival
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id3"}, context),
            cf::Result::kAllow);
  // Limited but in other airport
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id4"}, context),
            cf::Result::kAllow);
}

TEST_F(AirportEntryLimitTest, DestinationInAirport) {
  const auto filled_cache = CreateCache();
  UpdateCache(filled_cache, kEkbMainZone,
              {
                  {"driver_id2", Time(300)},
                  {"driver_id3", Time(150)},
              });
  const auto order_eta = std::chrono::seconds(50);
  SetFetchRouteInfo(std::chrono::seconds(10));
  const cfe::AirportEntryLimit filter(kEmptyInfo, filled_cache, now, {},
                                      MakeEntryLimitZone(kEkbMainZone),
                                      order_eta);
  // Not limited
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id1"}, context),
            cf::Result::kAllow);
  // Limited
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id2"}, context),
            cf::Result::kDisallow);
  // Limit drops before arrival
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id3"}, context),
            cf::Result::kAllow);
}

TEST_F(AirportEntryLimitTest, BothPointsInAirport) {
  const auto filled_cache = CreateCache();
  UpdateCache(filled_cache, kEkbMainZone,
              {
                  {"driver_id2", Time(300)},
                  {"driver_id3", Time(140)},
                  {"driver_id4", Time(140)},
                  {"driver_id6", Time(140)},
              });
  UpdateCache(filled_cache, kVkoMainZone,
              {
                  {"driver_id4", Time(300)},
                  {"driver_id5", Time(200)},
                  {"driver_id6", Time(200)},
              });
  const auto order_eta = std::chrono::seconds(60);
  SetFetchRouteInfo(std::chrono::seconds(30));
  const cfe::AirportEntryLimit filter(
      kEmptyInfo, filled_cache, now, MakeEntryLimitZone(kEkbMainZone),
      MakeEntryLimitZone(kVkoMainZone), order_eta);
  // Not limited
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id1"}, context),
            cf::Result::kAllow);
  // Limited at source
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id2"}, context),
            cf::Result::kDisallow);
  // Limit at source drops
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id3"}, context),
            cf::Result::kAllow);
  // Limit at source drops, Limited at destination
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id4"}, context),
            cf::Result::kDisallow);
  // Limit at destination drops
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id5"}, context),
            cf::Result::kAllow);
  // Both limits drop
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id6"}, context),
            cf::Result::kAllow);
}

TEST_F(AirportEntryLimitTest, EntryLimitTimeSettings) {
  const auto filled_cache = CreateCache();
  UpdateCache(filled_cache, kEkbMainZone,
              {
                  {"driver_id2", Time(300)},
                  {"driver_id3", Time(130)},
                  {"driver_id4", Time(140)},
              });
  UpdateCache(filled_cache, kVkoMainZone,
              {
                  {"driver_id5", Time(180)},
                  {"driver_id6", Time(200)},
              });
  const auto order_eta = std::chrono::seconds(60);
  SetFetchRouteInfo(std::chrono::seconds(30));
  const cfe::AirportEntryLimit filter(
      kEmptyInfo, filled_cache, now, MakeEntryLimitZone(kEkbMainZone, 10, 0.1),
      MakeEntryLimitZone(kVkoMainZone, 10, 0.1), order_eta);
  // Limited at source
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id2"}, context),
            cf::Result::kDisallow);
  // Limit at source drops
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id3"}, context),
            cf::Result::kAllow);
  // Limit at source doesn't drop with config
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id4"}, context),
            cf::Result::kDisallow);
  // Limit at destination drops
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id5"}, context),
            cf::Result::kAllow);
  // Limit at destination doesn't drop with config
  EXPECT_EQ(filter.Process(candidates::GeoMember{{}, "driver_id6"}, context),
            cf::Result::kDisallow);
}
