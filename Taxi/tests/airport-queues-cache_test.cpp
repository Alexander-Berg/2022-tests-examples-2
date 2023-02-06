#include <random>
#include <set>

#include <gtest/gtest.h>
#include <boost/functional/hash.hpp>

#include <dispatch-airport-queues-cache/dispatch-airport-queues-cache.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

namespace handle = clients::dispatch_airport::v1_active_drivers_queues::get;
namespace models = dispatch_airport_queues_cache::models;

using FilteredDriverInfo =
    dispatch_airport_queues_cache::driver_info::FilteredDriverInfo;
using EnteredDriverInfo =
    dispatch_airport_queues_cache::driver_info::EnteredDriverInfo;
using EntryLimitReachedDriverInfo =
    dispatch_airport_queues_cache::driver_info::EntryLimitReachedDriverInfo;

const std::string kDomodedovo{"dme"};
const std::string kVnukovo{"vko"};
const std::string kEkb{"ekb"};
const std::vector<std::string> kFallbackMainZones{};
const std::chrono::seconds kFilteredDriversTtl{10};

struct Less {
  bool operator()(const model::DriverInfo& lhs,
                  const model::DriverInfo& rhs) const {
    return std::tie(lhs.main_area, lhs.class_name, lhs.driver_id) <
           std::tie(rhs.main_area, rhs.class_name, rhs.driver_id);
  }
};

using DriversSet = std::set<model::DriverInfo, Less>;

handle::Response GenerateResponse(
    const std::chrono::system_clock::time_point& queued,
    const std::chrono::system_clock::duration& offset) {
  handle::Response response;
  response.queues = {{"econom",
                      {
                          {"driver2", queued},
                          {"driver5", queued},
                          {"driver1", queued + offset},
                          {"driver3", queued + offset},
                          {"driver4", queued + offset},
                      },
                      0},
                     {"business",
                      {{"driver6", queued},
                       {"driver2", queued},
                       {"driver4", queued},
                       {"driver3", queued + offset}},
                      10},
                     {"vip1",
                      {{"driver5", queued},
                       {"driver8", queued},
                       {"driver7", queued + offset},
                       {"driver3", queued + offset}},
                      std::nullopt}};
  return response;
}

DriversSet ToDriversSet(const handle::Response& response,
                        const std::string& main_area) {
  DriversSet result;
  for (const auto& queue : response.queues) {
    const auto& class_name = queue.tariff;
    for (std::size_t i = 0; i < queue.active_drivers.size(); i++) {
      const auto& driver = queue.active_drivers[i];
      result.emplace(model::DriverInfo{driver.dbid_uuid, main_area, class_name,
                                       i, driver.queued, false});
    }
  }
  return result;
}

void CompareSets(const DriversSet& lhs, const DriversSet& rhs) {
  EXPECT_EQ(lhs.size(), rhs.size());
  auto lit = lhs.begin(), rit = rhs.begin();
  while (lit != lhs.end() && rit != rhs.end()) {
    EXPECT_EQ(std::tie(lit->main_area, lit->class_name, lit->driver_id),
              std::tie(rit->main_area, rit->class_name, rit->driver_id));
    ++lit, ++rit;
  }
}

void CompareSetsWithQueuedInfo(const DriversSet& lhs, const DriversSet& rhs) {
  EXPECT_EQ(lhs.size(), rhs.size());
  auto lit = lhs.begin(), rit = rhs.begin();
  while (lit != lhs.end() && rit != rhs.end()) {
    EXPECT_EQ(std::tie(lit->main_area, lit->class_name, lit->driver_id,
                       lit->queued, lit->position, lit->is_check_in),
              std::tie(rit->main_area, rit->class_name, rit->driver_id,
                       rit->queued, rit->position, rit->is_check_in));
    ++lit, ++rit;
  }
}

DriversSet ToDriversSet(const model::AirportQueuesModel& airport_queues_model,
                        const std::string& main_area) {
  DriversSet result;
  auto [it, end] =
      airport_queues_model.GetMainZoneIndex().equal_range(main_area);
  while (it != end) {
    result.insert(*it);
    ++it;
  }
  return result;
}

template <typename Range>
DriversSet ToDriversSet(Range range) {
  DriversSet result;
  for (auto it = range.first; it != range.second; ++it) {
    result.insert(it->driver_info_ref.get());
  }
  return result;
}

void CheckUpdate(handle::Response response, const std::string& main_area) {
  auto lhs = ToDriversSet(response, main_area);
  model::AirportQueuesModel airport_queues_model{{}, {}};
  airport_queues_model.Update(main_area, false, false, kFallbackMainZones,
                              kFilteredDriversTtl, std::move(response));
  auto rhs = ToDriversSet(airport_queues_model, main_area);
  CompareSets(lhs, rhs);
}

std::string MakeRandomString(std::size_t length) {
  constexpr std::string_view kAbc{
      "abcdefghijklmnopqrstuvwxyz"
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"};

  std::random_device random_device{};
  using Distribution = std::uniform_int_distribution<std::size_t>;

  std::string result;
  result.resize(length);

  Distribution distribution{0, kAbc.length() - 1};
  for (char& c : result) {
    c = kAbc[distribution(random_device)];
  }

  return result;
}

handle::Response MakeRandomResponse(std::size_t queues_count,
                                    std::size_t drivers_count,
                                    std::size_t string_length) {
  handle::Response result;
  if (queues_count && drivers_count) {
    result.queues.resize(queues_count);
    for (auto& queue : result.queues) {
      queue.tariff = MakeRandomString(string_length);
      queue.active_drivers.resize(drivers_count);
      for (auto& driver : queue.active_drivers) {
        driver.dbid_uuid = MakeRandomString(string_length);
        driver.queued = std::chrono::system_clock::now();
      }
    }
  }

  return result;
}

TEST(AirportQueuesModel, Update) {
  CheckUpdate(MakeRandomResponse(15, 20, 15), kDomodedovo);

  handle::Response response_domodedovo_empty;
  response_domodedovo_empty.queues = {};
  CheckUpdate(response_domodedovo_empty, kDomodedovo);
  for (std::size_t i = 0; i < 10; ++i) {
    CheckUpdate(MakeRandomResponse(35, 100, 15), kVnukovo);
  }
}

void CheckFindDrivers(const std::chrono::system_clock::time_point& now,
                      const std::chrono::system_clock::duration& offset,
                      const std::vector<std::string>& dispatch_classes_order,
                      const DriversSet& expected_drivers_set) {
  // 1. driver1 only in econom, queued without offset
  // 2. driver2 in business and econom, queued without offset. classes order
  // matters
  // 3. driver3 in all tariffs, queued with offset. classes order matters
  // 4. driver4 in business without offset and in econom with offset, classes
  // order must not matter
  // 5. driver5 in vip1 and econom, queued without offset. classes order matters
  // 6. driver6 only in business, queued without offset
  // 7. driver7 only vip1, queued with offset
  // 8. driver8 only vip1, queued without offset
  handle::Response response = GenerateResponse(now, offset);
  model::AirportQueuesModel airport_queues_model{{}, dispatch_classes_order};
  airport_queues_model.Update(kDomodedovo, false, false, kFallbackMainZones,
                              kFilteredDriversTtl, std::move(response));
  const std::vector<std::string> classes{"econom", "business", "vip1"};
  auto drivers_view = airport_queues_model.FindDrivers(kDomodedovo, classes);

  auto& queued_index = drivers_view.get<model::OrderedDriverInfo::ByQueued>();
  auto queued_range = std::pair(queued_index.begin(), queued_index.end());
  ASSERT_TRUE(std::is_sorted(
      queued_range.first, queued_range.second,
      [](const auto lhs, const auto rhs) {
        const auto& left_driver_info = lhs.driver_info_ref.get();
        const auto& right_driver_info = rhs.driver_info_ref.get();
        return lhs.priority == rhs.priority &&
               left_driver_info.position < right_driver_info.position &&
               lhs.GetQueued() < rhs.GetQueued();
      }));

  DriversSet test_driver_set = ToDriversSet(queued_range);
  CompareSetsWithQueuedInfo(expected_drivers_set, test_driver_set);
}

TEST(AirportQueuesModel, FindDrivers) {
  const auto now = std::chrono::system_clock::now();
  const std::chrono::system_clock::duration offset(
      std::chrono::duration<int>(1));

  const std::vector<std::string> order1 = {"business", "econom", "vip1"};
  const DriversSet expected_drivers_set1 = {
      {"driver1", kDomodedovo, "econom", 2, now + offset, false},
      {"driver2", kDomodedovo, "econom", 0, now, false},
      {"driver3", kDomodedovo, "vip1", 3, now + offset, false},
      {"driver4", kDomodedovo, "business", 2, now, false},
      {"driver5", kDomodedovo, "vip1", 0, now, false},
      {"driver6", kDomodedovo, "business", 0, now, false},
      {"driver7", kDomodedovo, "vip1", 2, now + offset, false},
      {"driver8", kDomodedovo, "vip1", 1, now, false},
  };
  CheckFindDrivers(now, offset, order1, expected_drivers_set1);

  const std::vector<std::string> order2 = {"econom", "vip1"};
  CheckFindDrivers(now, offset, order2, expected_drivers_set1);

  const std::vector<std::string> order3 = {"vip1", "business", "econom"};
  const DriversSet expected_drivers_set3 = {
      {"driver1", kDomodedovo, "econom", 2, now + offset},
      {"driver2", kDomodedovo, "econom", 0, now},
      {"driver3", kDomodedovo, "econom", 3, now + offset},
      {"driver4", kDomodedovo, "business", 2, now},
      {"driver5", kDomodedovo, "econom", 1, now},
      {"driver6", kDomodedovo, "business", 0, now},
      {"driver7", kDomodedovo, "vip1", 2, now + offset},
      {"driver8", kDomodedovo, "vip1", 1, now},
  };
  CheckFindDrivers(now, offset, order3, expected_drivers_set3);

  const std::vector<std::string> order4 = {"business", "econom"};
  CheckFindDrivers(now, offset, order4, expected_drivers_set3);
}

TEST(AirportQueuesModel, MainZoneInfo) {
  model::AirportQueuesModel airport_queues_model{{}, {}};
  const auto now = std::chrono::system_clock::now();
  const std::chrono::minutes offset{1};
  airport_queues_model.Update(kDomodedovo, false, false, kFallbackMainZones,
                              kFilteredDriversTtl,
                              GenerateResponse(now, offset));
  ASSERT_EQ(airport_queues_model.GetMainZoneInfo("unknown_main_zone"),
            std::nullopt);
  ASSERT_EQ(
      airport_queues_model.GetMainZoneTariffInfo(kDomodedovo, "unknown_tariff"),
      std::nullopt);
  ASSERT_EQ(airport_queues_model.GetMainZoneTariffInfo("unknown_main_zone",
                                                       "unknown_tariff"),
            std::nullopt);

  auto dme_etalon = models::MainZoneInfo{
      models::TariffInfos{{"econom", models::TariffInfo{0}},
                          {"business", models::TariffInfo{10}},
                          {"vip1", models::TariffInfo{std::nullopt}}},
      false, kFallbackMainZones};

  ASSERT_EQ(airport_queues_model.GetMainZoneInfo(kDomodedovo), dme_etalon);
  ASSERT_EQ(airport_queues_model.GetMainZoneTariffInfo(kDomodedovo, "econom"),
            dme_etalon.tariff_infos["econom"]);
  ASSERT_EQ(airport_queues_model.GetMainZoneTariffInfo(kDomodedovo, "business"),
            dme_etalon.tariff_infos["business"]);
  ASSERT_EQ(airport_queues_model.GetMainZoneTariffInfo(kDomodedovo, "vip1"),
            dme_etalon.tariff_infos["vip1"]);

  const auto expected_main_zone_infos =
      models::MainZoneInfos{{kDomodedovo, dme_etalon}};
  ASSERT_EQ(airport_queues_model.GetMainZoneInfos(), expected_main_zone_infos);
}

TEST(AirportQueuesModel, FindDriversWithPriority) {
  const auto now = std::chrono::system_clock::now();
  const std::chrono::system_clock::duration offset(
      std::chrono::duration<int>(1));

  const std::vector<std::string> order1 = {"econom"};
  handle::Response response_dme;
  response_dme.queues = {
      {"econom", {{"driver1", now}, {"driver2", now + offset}}, 0}};
  handle::Response response_ekb;
  response_ekb.queues = {
      {"econom", {{"driver5", now}, {"driver6", now + offset}}, 0}};

  model::AirportQueuesModel airport_queues_model{{}, {}};
  airport_queues_model.Update(kDomodedovo, false, false, {},
                              kFilteredDriversTtl, std::move(response_dme));
  airport_queues_model.Update(kEkb, false, false, {}, kFilteredDriversTtl,
                              std::move(response_ekb));
  const std::vector<std::string> classes{"econom"};

  const auto check_fallback_search =
      [&](std::vector<std::string> fallback_search_main_areas,
          const std::vector<std::string>& etalon) {
        handle::Response response_vko;
        response_vko.queues = {
            {"econom", {{"driver3", now}, {"driver4", now + offset}}, 0}};
        airport_queues_model.Update(
            kVnukovo, true, false, std::move(fallback_search_main_areas),
            kFilteredDriversTtl, std::move(response_vko));

        auto drivers_view = airport_queues_model.FindDrivers(kVnukovo, classes);
        auto& queued_index =
            drivers_view.get<model::OrderedDriverInfo::ByQueued>();
        auto queued_range = std::pair(queued_index.begin(), queued_index.end());
        std::vector<std::string> ordered_drivers;
        for (auto it = queued_range.first; it != queued_range.second; ++it) {
          const auto& info = it->driver_info_ref.get();
          ordered_drivers.emplace_back(info.driver_id);
        }
        ASSERT_EQ(ordered_drivers, etalon);
        ASSERT_TRUE(std::is_sorted(queued_range.first, queued_range.second,
                                   [](const auto lhs, const auto rhs) {
                                     return lhs.priority >= rhs.priority &&
                                            lhs.GetQueued() < rhs.GetQueued();
                                   }));

        const DriversSet test_driver_set = ToDriversSet(queued_range);
        const DriversSet expected_drivers_set = {
            {"driver4", kVnukovo, "econom", 1, now + offset, true},
            {"driver3", kVnukovo, "econom", 0, now, true},
            {"driver2", kDomodedovo, "econom", 1, now + offset, false},
            {"driver1", kDomodedovo, "econom", 0, now, false},
            {"driver6", kEkb, "econom", 1, now + offset, false},
            {"driver5", kEkb, "econom", 0, now, false},
        };
        CompareSetsWithQueuedInfo(expected_drivers_set, test_driver_set);
      };

  check_fallback_search(
      {kVnukovo, kDomodedovo, kEkb},
      {"driver3", "driver4", "driver1", "driver2", "driver5", "driver6"});
  check_fallback_search(
      {kVnukovo, kEkb, kDomodedovo},
      {"driver3", "driver4", "driver5", "driver6", "driver1", "driver2"});
}

TEST(AirportQueuesModel, TestFilteredDrivers) {
  const auto check_filtered_drivers = [](auto& response, const auto& etalon) {
    std::sort(response.begin(), response.end(),
              [&](const auto& first, const auto& second) {
                return first.driver_id < second.driver_id;
              });
    ASSERT_EQ(response.size(), etalon.size());
    for (size_t i = 0; i < response.size(); ++i) {
      const auto& lhs = response[i];
      const auto& rhs = etalon[i];
      ASSERT_EQ(
          std::tie(lhs.driver_id, lhs.main_area, lhs.reason, lhs.updated),
          std::tie(rhs.driver_id, rhs.main_area, rhs.reason, rhs.updated));
    }
  };

  handle::Response response_dme;
  response_dme.filtered = {{"driver_1", "user_cancel"},
                           {"driver_2", "user_cancel"},
                           {"driver_3", "user_cancel"}};

  handle::Response response_vko;
  response_vko.filtered = {{"driver_4", "driver_cancel"},
                           {"driver_5", "driver_cancel"},
                           {"driver_6", "driver_cancel"}};

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  model::AirportQueuesModel airport_queues_model{{}, {}};
  airport_queues_model.Update(kDomodedovo, false, false, {},
                              kFilteredDriversTtl, std::move(response_dme));
  airport_queues_model.Update(kVnukovo, false, false, {}, kFilteredDriversTtl,
                              std::move(response_vko));
  const auto& filtered_idx = airport_queues_model.GetFilteredDriverIdIndex();
  std::vector<FilteredDriverInfo> filtered_driver_info;
  for (auto it = filtered_idx.cbegin(); it != filtered_idx.cend(); ++it) {
    filtered_driver_info.emplace_back(*it);
  }
  check_filtered_drivers(filtered_driver_info,
                         std::vector<FilteredDriverInfo>{
                             {"driver_1", kDomodedovo, "user_cancel", now},
                             {"driver_2", kDomodedovo, "user_cancel", now},
                             {"driver_3", kDomodedovo, "user_cancel", now},
                             {"driver_4", kVnukovo, "driver_cancel", now},
                             {"driver_5", kVnukovo, "driver_cancel", now},
                             {"driver_6", kVnukovo, "driver_cancel", now}});

  filtered_driver_info.clear();
  auto range =
      airport_queues_model.GetFilteredMainZoneIndex().equal_range(kDomodedovo);
  while (range.first != range.second) {
    filtered_driver_info.emplace_back(*range.first);
    ++range.first;
  }
  check_filtered_drivers(filtered_driver_info,
                         std::vector<FilteredDriverInfo>{
                             {"driver_1", kDomodedovo, "user_cancel", now},
                             {"driver_2", kDomodedovo, "user_cancel", now},
                             {"driver_3", kDomodedovo, "user_cancel", now},
                         });

  // sleep 6s, new filtered drivers added to vko
  auto sleep_sec = std::chrono::seconds{6};
  utils::datetime::MockNowSet(now + sleep_sec);
  response_dme.filtered = {
      {"driver_3", "user_cancel"},
      {"driver_7", "blacklist"},
      {"driver_8", "blacklist"},
      {"driver_9", "blacklist"},
  };
  airport_queues_model.Update(kDomodedovo, false, false, {},
                              kFilteredDriversTtl, std::move(response_dme));
  filtered_driver_info.clear();
  range =
      airport_queues_model.GetFilteredMainZoneIndex().equal_range(kDomodedovo);
  while (range.first != range.second) {
    filtered_driver_info.emplace_back(*range.first);
    ++range.first;
  }
  check_filtered_drivers(
      filtered_driver_info,
      std::vector<FilteredDriverInfo>{
          {"driver_1", kDomodedovo, "user_cancel", now},
          {"driver_2", kDomodedovo, "user_cancel", now},
          {"driver_3", kDomodedovo, "user_cancel", now + sleep_sec},
          {"driver_7", kDomodedovo, "blacklist", now + sleep_sec},
          {"driver_8", kDomodedovo, "blacklist", now + sleep_sec},
          {"driver_9", kDomodedovo, "blacklist", now + sleep_sec},
      });

  // sleep 6s, check removed drivers
  utils::datetime::MockNowSet(now + 2 * sleep_sec);
  response_dme.filtered = {
      {"driver_10", "blacklist"},
      {"driver_11", "blacklist"},
  };
  airport_queues_model.Update(kDomodedovo, false, false, {},
                              kFilteredDriversTtl, std::move(response_dme));
  filtered_driver_info.clear();
  range =
      airport_queues_model.GetFilteredMainZoneIndex().equal_range(kDomodedovo);
  while (range.first != range.second) {
    filtered_driver_info.emplace_back(*range.first);
    ++range.first;
  }
  check_filtered_drivers(
      filtered_driver_info,
      std::vector<FilteredDriverInfo>{
          {"driver_10", kDomodedovo, "blacklist", now + 2 * sleep_sec},
          {"driver_11", kDomodedovo, "blacklist", now + 2 * sleep_sec},
          {"driver_3", kDomodedovo, "user_cancel", now + sleep_sec},
          {"driver_7", kDomodedovo, "blacklist", now + sleep_sec},
          {"driver_8", kDomodedovo, "blacklist", now + sleep_sec},
          {"driver_9", kDomodedovo, "blacklist", now + sleep_sec},
      });
}

void CheckEntryLimitDriver(const EntryLimitReachedDriverInfo& lhs,
                           const EntryLimitReachedDriverInfo& rhs) {
  ASSERT_EQ(std::tie(lhs.driver_id, lhs.main_area, lhs.limit_end_ts),
            std::tie(rhs.driver_id, rhs.main_area, rhs.limit_end_ts));
}

void CheckEntryLimitDriversByMainZone(
    model::AirportQueuesModel& airport_queues_model,
    const std::string& main_zone, handle::Response&& dispatch_airport_response,
    const std::vector<EntryLimitReachedDriverInfo>& added_etalon,
    const std::vector<EntryLimitReachedDriverInfo>& total_etalon) {
  const auto check_result = [](auto& response, const auto& etalon) {
    std::sort(response.begin(), response.end(),
              [&](const auto& first, const auto& second) {
                if (first.driver_id != second.driver_id)
                  return first.driver_id < second.driver_id;
                return first.main_area < second.main_area;
              });
    ASSERT_EQ(response.size(), etalon.size());
    for (size_t i = 0; i < response.size(); ++i) {
      CheckEntryLimitDriver(response[i], etalon[i]);
    }
  };
  airport_queues_model.Update(main_zone, false, false, {}, kFilteredDriversTtl,
                              std::move(dispatch_airport_response));

  const auto& entry_limit_idx =
      airport_queues_model.GetEntryLimitReachedMainZoneIndex();
  std::vector<EntryLimitReachedDriverInfo> info;
  for (auto it = entry_limit_idx.cbegin(); it != entry_limit_idx.cend(); ++it) {
    info.emplace_back(*it);
  }
  check_result(info, total_etalon);

  info.clear();
  auto range = entry_limit_idx.equal_range(main_zone);
  while (range.first != range.second) {
    info.emplace_back(*range.first);
    ++range.first;
  }
  check_result(info, added_etalon);
}

void CheckEntryLimitDriverByMainZoneDriverId(
    const model::AirportQueuesModel& airport_queues_model,
    const EntryLimitReachedDriverInfo& etalon) {
  const auto& entry_limit_idx =
      airport_queues_model.GetEntryLimitReachedMainZoneDriverIdIndex();
  const auto result =
      entry_limit_idx.find(std::tie(etalon.main_area, etalon.driver_id));
  ASSERT_TRUE(result != entry_limit_idx.cend());
  CheckEntryLimitDriver(*result, etalon);
}

TEST(AirportQueuesModel, TestEntryLimitedDrivers) {
  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);
  model::AirportQueuesModel airport_queues_model{{}, {}, false, true};

  handle::Response response_dme;
  response_dme.entry_limit_reached = {
      {"driver_1", now + std::chrono::seconds(60)},
      {"driver_2", now + std::chrono::seconds(120)}};
  std::vector<EntryLimitReachedDriverInfo> total_etalon =
      std::vector<EntryLimitReachedDriverInfo>{
          {kDomodedovo, "driver_1", now + std::chrono::seconds(60)},
          {kDomodedovo, "driver_2", now + std::chrono::seconds(120)}};
  CheckEntryLimitDriversByMainZone(airport_queues_model, kDomodedovo,
                                   std::move(response_dme), total_etalon,
                                   total_etalon);

  CheckEntryLimitDriverByMainZoneDriverId(
      airport_queues_model,
      {kDomodedovo, "driver_2", now + std::chrono::seconds(120)});
  const auto& entry_limit_idx =
      airport_queues_model.GetEntryLimitReachedMainZoneDriverIdIndex();
  const auto result = entry_limit_idx.find(std::tie(kVnukovo, "driver_2"));
  ASSERT_TRUE(result == entry_limit_idx.cend());

  handle::Response response_vko;
  response_vko.entry_limit_reached = {
      {"driver_2", now + std::chrono::seconds(30)},
      {"driver_3", now + std::chrono::seconds(999)}};
  std::vector<EntryLimitReachedDriverInfo> vko_added_etalon = {
      {kVnukovo, "driver_2", now + std::chrono::seconds(30)},
      {kVnukovo, "driver_3", now + std::chrono::seconds(999)}};
  total_etalon.push_back(
      {kVnukovo, "driver_2", now + std::chrono::seconds(30)});
  total_etalon.push_back(
      {kVnukovo, "driver_3", now + std::chrono::seconds(999)});
  CheckEntryLimitDriversByMainZone(airport_queues_model, kVnukovo,
                                   std::move(response_vko), vko_added_etalon,
                                   total_etalon);

  CheckEntryLimitDriverByMainZoneDriverId(
      airport_queues_model,
      {kDomodedovo, "driver_2", now + std::chrono::seconds(120)});
  CheckEntryLimitDriverByMainZoneDriverId(
      airport_queues_model,
      {kVnukovo, "driver_2", now + std::chrono::seconds(30)});

  handle::Response response_dme_empty;
  response_dme.entry_limit_reached = {};
  CheckEntryLimitDriversByMainZone(airport_queues_model, kDomodedovo,
                                   std::move(response_dme_empty), {},
                                   vko_added_etalon);
}

void CheckEnteredDriverByDriverId(
    const model::AirportQueuesModel& airport_queues_model,
    const std::string driver_id,
    const std::optional<EnteredDriverInfo> etalon) {
  const auto& entered_idx = airport_queues_model.GetEnteredDriverIdIndex();
  const auto result = entered_idx.find(driver_id);
  if (etalon) {
    ASSERT_TRUE(result != entered_idx.cend());
    ASSERT_EQ(std::tie(result->driver_id, result->main_area),
              std::tie(etalon->driver_id, etalon->main_area));
  } else {
    ASSERT_TRUE(result == entered_idx.cend());
  }
}

TEST(AirportQueuesModel, TestEnteredDrivers) {
  model::AirportQueuesModel airport_queues_model{{}, {}, true, false};

  handle::Response response_dme;
  response_dme.entered = {{"driver_1"}, {"driver_2"}};
  airport_queues_model.Update(kDomodedovo, false, false, {},
                              kFilteredDriversTtl, std::move(response_dme));

  CheckEnteredDriverByDriverId(airport_queues_model, "driver_1",
                               {{kDomodedovo, "driver_1"}});
  CheckEnteredDriverByDriverId(airport_queues_model, "driver_2",
                               {{kDomodedovo, "driver_2"}});
  CheckEnteredDriverByDriverId(airport_queues_model, "driver_3", std::nullopt);

  handle::Response response_vko;
  response_vko.entered = {{"driver_3"}};
  airport_queues_model.Update(kVnukovo, false, false, {}, kFilteredDriversTtl,
                              std::move(response_vko));

  CheckEnteredDriverByDriverId(airport_queues_model, "driver_1",
                               {{kDomodedovo, "driver_1"}});
  CheckEnteredDriverByDriverId(airport_queues_model, "driver_2",
                               {{kDomodedovo, "driver_2"}});
  CheckEnteredDriverByDriverId(airport_queues_model, "driver_3",
                               {{kVnukovo, "driver_3"}});

  handle::Response response_dme_empty;
  response_dme.entry_limit_reached = {};
  airport_queues_model.Update(kDomodedovo, false, false, {},
                              kFilteredDriversTtl,
                              std::move(response_dme_empty));

  CheckEnteredDriverByDriverId(airport_queues_model, "driver_1", std::nullopt);
  CheckEnteredDriverByDriverId(airport_queues_model, "driver_2", std::nullopt);
  CheckEnteredDriverByDriverId(airport_queues_model, "driver_3",
                               {{kVnukovo, "driver_3"}});
}

}  // namespace
