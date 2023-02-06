#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>
#include <userver/utils/algo.hpp>
#include <userver/utils/datetime.hpp>

#include <grocery-depots-client/models/delivery_zones_cache.hpp>
#include <grocery-depots-client/models/depots_cache.hpp>

using namespace grocery_depots_client;

namespace {

void EnsureEqual(const grocery_depots::models::Depot& lhs,
                 const grocery_depots::models::Depot& rhs) {
  EXPECT_EQ(lhs.id, rhs.id);
  EXPECT_EQ(lhs.legacy_id, rhs.legacy_id);
  EXPECT_EQ(lhs.country_iso3, rhs.country_iso3);
  EXPECT_EQ(lhs.country_iso2, rhs.country_iso2);
  EXPECT_EQ(lhs.region_id, rhs.region_id);
  EXPECT_EQ(lhs.timezone, rhs.timezone);
  EXPECT_EQ(lhs.location, rhs.location);
  EXPECT_EQ(lhs.address, rhs.address);
  EXPECT_EQ(lhs.tin, rhs.tin);
  EXPECT_EQ(lhs.phone_number, rhs.phone_number);
  EXPECT_EQ(lhs.email, rhs.email);
  EXPECT_EQ(lhs.directions, rhs.directions);
  EXPECT_EQ(lhs.currency, rhs.currency);
  EXPECT_EQ(lhs.company_id, rhs.company_id);
  EXPECT_EQ(lhs.company_type, rhs.company_type);
  EXPECT_EQ(lhs.company_title, rhs.company_title);
  EXPECT_EQ(lhs.allow_parcels, rhs.allow_parcels);
  EXPECT_EQ(lhs.name, rhs.name);
  EXPECT_EQ(lhs.short_address, rhs.short_address);
  EXPECT_EQ(lhs.status, rhs.status);
  EXPECT_EQ(lhs.hidden, rhs.hidden);
  EXPECT_EQ(lhs.telegram, rhs.telegram);
  EXPECT_EQ(lhs.root_category_id, rhs.root_category_id);
  EXPECT_EQ(lhs.assortment_id, rhs.assortment_id);
  EXPECT_EQ(lhs.price_list_id, rhs.price_list_id);
  EXPECT_EQ(lhs.oebs_depot_id, rhs.oebs_depot_id);
  EXPECT_EQ(lhs.company_actual_address, rhs.company_actual_address);
  EXPECT_EQ(lhs.timetable, rhs.timetable);
}

void EnsureEqual(const grocery_depots::models::DeliveryZone& lhs,
                 const grocery_depots::models::DeliveryZone& rhs) {
  EXPECT_EQ(lhs.zone_id, rhs.zone_id);
  EXPECT_EQ(lhs.depot_id, rhs.depot_id);
  EXPECT_EQ(lhs.delivery_type, rhs.delivery_type);
  EXPECT_EQ(lhs.zone_status, rhs.zone_status);
  EXPECT_EQ(lhs.timetable, rhs.timetable);
  EXPECT_EQ(lhs.effective_from, rhs.effective_from);
  EXPECT_EQ(lhs.effective_till, rhs.effective_till);

  std::equal(
      lhs.geozone.GetMultiPolygon().begin(),
      lhs.geozone.GetMultiPolygon().end(),
      rhs.geozone.GetMultiPolygon().begin(),
      rhs.geozone.GetMultiPolygon().end(),
      [](const grocery_depots::models::DeliveryZoneGeometry::Polygon& lhs,
         const grocery_depots::models::DeliveryZoneGeometry::Polygon& rhs) {
        EXPECT_EQ(lhs.outer(), rhs.outer());
        EXPECT_EQ(lhs.inners(), rhs.inners());
        return true;
      });
}

std::size_t GetDeliveryZonesCacheSize(
    const models::DeliveryZonesCache& zones_cache) {
  return zones_cache.GetZones().size();
}

grocery_depots::models::DeliveryZoneGeometry::Polygon MakePolygon(
    std::size_t idx) {
  const auto make_pos = [](double lat, double lon) {
    return geometry::Position(lat * geometry::lat, lon * geometry::lon);
  };

  const auto fill_ring = [&make_pos](std::vector<geometry::Position>& ring,
                                     std::size_t idx) {
    ring.push_back(make_pos(idx + 1, idx));
    ring.push_back(make_pos(idx + 1, idx + 1));
    ring.push_back(make_pos(idx, idx + 1));
    ring.push_back(make_pos(idx, idx));
  };

  grocery_depots::models::DeliveryZoneGeometry::Polygon result;
  fill_ring(result.outer(), idx);

  fill_ring(result.inners().emplace_back(), idx + 11);
  fill_ring(result.inners().emplace_back(), idx + 12);
  fill_ring(result.inners().emplace_back(), idx + 13);
  fill_ring(result.inners().emplace_back(), idx + 14);
  fill_ring(result.inners().emplace_back(), idx + 15);

  return result;
}

}  // namespace

TEST(CacheDumpTest, TestEmptyDepotsCache) {
  const models::DepotsCache written_depots_cache({});

  const auto buffer = dump::ToBinary(written_depots_cache);
  const models::DepotsCache read_depots_cache =
      dump::FromBinary<models::DepotsCache>(buffer);

  ASSERT_EQ(0, written_depots_cache.GetSize());
  ASSERT_EQ(0, read_depots_cache.GetSize());
}

TEST(CacheDumpTest, TestEmptyDeliveryZonesCache) {
  const models::DeliveryZonesCache written_zones_cache({});

  const auto buffer = dump::ToBinary(written_zones_cache);

  dump::MockReader reader(std::move(buffer));
  const auto read_zones_cache = reader.Read<models::DeliveryZonesCache>();
  reader.Finish();

  ASSERT_EQ(0, GetDeliveryZonesCacheSize(written_zones_cache));
  ASSERT_EQ(0, GetDeliveryZonesCacheSize(read_zones_cache));
}

TEST(CacheDumpTest, TestDepotsCacheBasic) {
  const std::vector reference_depots{
      grocery_depots::models::Depot{
          grocery_shared::DepotId{"test_depot_0"},         /* id */
          grocery_shared::LegacyDepotId{"legacy_depot_0"}, /* legacy_id */
          grocery_shared::CountryIso3{"ISR"},              /* country_iso3 */
          grocery_shared::CountryIso2{"IL"},               /* country_iso2 */
          777,                                             /* region_id */
          "utc",                                           /* timezone */

          geometry::PositionAsObject{geometry::Position{
              12.0 * geometry::lat, 87.0 * geometry::lon}},  /* location */
          "Адрес кириллицей, чтобы жизнь медом не казалась", /* address */
          "245678121",                                       /* tin */
          grocery_shared::PhoneNumber{"+7987654321"},        /* phone_number */
          "test@yandex.ru",                                  /* email */
          "Кириллицы много не бывает",                       /* directions */
          "ILS",                                             /* currency */
          grocery_shared::CompanyId{"test_company_id"},      /* company_id */
          grocery_shared::CompanyType::kYandex,              /* company_type */
          "ООО Яндекс.Лавка",                                /* company_title */
          true,                                              /* allow_parcels */
          "test_name",                                       /* name */
          "Короткий адрес",                                  /* short_address */
          grocery_depots::models::Depot::Status::kActive,    /* status */
          false,                                             /* hidden */
          "@grocery_test",                                   /* telegram */
          grocery_shared::CategoryId{"test_category_id"}, /* root_category_id */

          grocery_shared::AssortmentId{
              "test_assortment_id"},                    /* assortment_id */
          grocery_shared::PriceListId{"price_list_id"}, /* price_list_id */
          "oebs_depot_id",                              /* oebs_depot_id */
          "115035, Россия, г. Москва, ул. Садовническая, д. 82, стр. 2, пом. "
          "3В21", /* company_actual_address */
          std::optional{
              std::vector<grocery_shared::datetime::TimeOfDayInterval>{
                  grocery_shared::datetime::TimeOfDayInterval{
                      grocery_shared::datetime::TimeOfDayInterval::DayType::
                          kEveryday,
                      grocery_shared::datetime::TimeOfDayInterval::Range{
                          grocery_shared::datetime::TimeOfDayInterval::Time{
                              std::chrono::minutes{10}},
                          grocery_shared::datetime::TimeOfDayInterval::Time{
                              std::chrono::minutes{20}}}}}} /* timetable */
      },
      grocery_depots::models::Depot{
          grocery_shared::DepotId{"test_depot_1"},         /* id */
          grocery_shared::LegacyDepotId{"legacy_depot_1"}, /* legacy_id */
          grocery_shared::CountryIso3{"RUS"},              /* country_iso3 */
          grocery_shared::CountryIso2{"RU"},               /* country_iso2 */
          121,                                             /* region_id */
          "utc",                                           /* timezone */

          geometry::PositionAsObject{geometry::Position{
              15.0 * geometry::lat, 33.0 * geometry::lon}}, /* location */
          "Москва, Тестовая улица, 21",                     /* address */
          "987273",                                         /* tin */
          grocery_shared::PhoneNumber{"+7555555555"},       /* phone_number */
          "test2@yandex.ru",                                /* email */
          std::nullopt,                                     /* directions */
          "RUB",                                            /* currency */
          grocery_shared::CompanyId{"test_company_id_1"},   /* company_id */
          grocery_shared::CompanyType::kFranchise,          /* company_type */
          "ООО Яндекс.Лавка.Но.Не.Совсем",                  /* company_title */
          false,                                            /* allow_parcels */
          "test_name_2",                                    /* name */
          "Тестовая улица, 21",                             /* short_address */
          grocery_depots::models::Depot::Status::kComingSoon, /* status */
          true,                                               /* hidden */
          "@grocery_test2",                                   /* telegram */
          std::nullopt, /* root_category_id */

          std::nullopt, /* assortment_id */
          std::nullopt, /* price_list_id */
          std::nullopt, /* oebs_depot_id */
          std::nullopt, /* company_actual_address */
          std::optional{
              std::vector<grocery_shared::datetime::TimeOfDayInterval>{
                  grocery_shared::datetime::TimeOfDayInterval{
                      grocery_shared::datetime::TimeOfDayInterval::DayType::
                          kEveryday,
                      grocery_shared::datetime::TimeOfDayInterval::Range{
                          grocery_shared::datetime::TimeOfDayInterval::Time{
                              std::chrono::minutes{10}},
                          grocery_shared::datetime::TimeOfDayInterval::Time{
                              std::chrono::minutes{20}}}}}} /* timetable */
      },
  };

  auto tmp = reference_depots;
  models::DepotsCache written_cache(std::move(tmp));

  const auto buffer = dump::ToBinary(written_cache);
  models::DepotsCache read_cache =
      dump::FromBinary<models::DepotsCache>(buffer);

  ASSERT_EQ(reference_depots.size(), read_cache.GetSize());
  const auto& read_depots = read_cache.GetDepots();

  for (std::size_t i = 0; i < reference_depots.size(); ++i) {
    EnsureEqual(reference_depots[i], read_depots[i].get());
  }
}

TEST(CacheDumpTest, TestDeliveryZonesCacheBasic) {
  grocery_depots::models::DeliveryZoneGeometry geozone_0{};
  auto& multipolygon_0 = geozone_0.GetMultiPolygon();
  for (std::size_t i = 0; i < 100; ++i) {
    multipolygon_0.push_back(MakePolygon(i));
  }

  grocery_depots::models::DeliveryZoneGeometry geozone_1{};
  auto& multipolygon_1 = geozone_1.GetMultiPolygon();
  for (std::size_t i = 3; i < 17; ++i) {
    multipolygon_1.push_back(MakePolygon(i));
  }

  std::vector intervals_0{
      grocery_shared::datetime::TimeOfDayInterval{
          grocery_shared::datetime::TimeOfDayInterval::DayType::kEveryday,
          grocery_shared::datetime::TimeOfDayInterval::Range{
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{10}},
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{20}}}},
      grocery_shared::datetime::TimeOfDayInterval{
          grocery_shared::datetime::TimeOfDayInterval::DayType::kThursday,
          grocery_shared::datetime::TimeOfDayInterval::Range{
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{1000}},
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{2500}}}},
      grocery_shared::datetime::TimeOfDayInterval{
          grocery_shared::datetime::TimeOfDayInterval::DayType::kSaturday,
          grocery_shared::datetime::TimeOfDayInterval::Range{
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{9000}},
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{6290}}}},
  };

  std::vector intervals_1{
      grocery_shared::datetime::TimeOfDayInterval{
          grocery_shared::datetime::TimeOfDayInterval::DayType::kHoliday,
          grocery_shared::datetime::TimeOfDayInterval::Range{
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{77}},
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{88}}}},
      grocery_shared::datetime::TimeOfDayInterval{
          grocery_shared::datetime::TimeOfDayInterval::DayType::kMonday,
          grocery_shared::datetime::TimeOfDayInterval::Range{
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{99}},
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{1010}}}},
      grocery_shared::datetime::TimeOfDayInterval{
          grocery_shared::datetime::TimeOfDayInterval::DayType::kWorkday,
          grocery_shared::datetime::TimeOfDayInterval::Range{
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{1111}},
              grocery_shared::datetime::TimeOfDayInterval::Time{
                  std::chrono::minutes{1212}}}},
  };

  std::vector reference_zones{
      grocery_depots::models::DeliveryZone{
          grocery_depots::models::ZoneId{"zone_id_0"}, /* zone_id */
          grocery_shared::DepotId{"depot_id_0"},       /* depot_id */
          grocery_shared::DeliveryType::kPedestrian,   /* delivery_type */
          grocery_depots::models::DeliveryZone::Status::kActive, /* zone_status
                                                                  */
          std::move(intervals_0),                                /* timetable */
          std::move(geozone_0),                                  /* geozone */
          std::nullopt, /* effective_from */
          std::nullopt  /* effective_till */
      },
      grocery_depots::models::DeliveryZone{
          grocery_depots::models::ZoneId{"zone_id_1"}, /* zone_id */
          grocery_shared::DepotId{"depot_id_1"},       /* depot_id */
          grocery_shared::DeliveryType::kRover,        /* delivery_type */
          grocery_depots::models::DeliveryZone::Status::
              kDisabled,          /* zone_status
                                   */
          std::move(intervals_1), /* timetable */
          std::move(geozone_1),   /* geozone */
          ::utils::datetime::Stringtime(
              "2021-11-19T21:34:13.854565956+0000"), /* effective_from */
          ::utils::datetime::Stringtime(
              "2021-11-19T22:33:00.854565972+0000") /* effective_till */
      },
  };

  const models::DeliveryZonesCache written_zones_cache(
      std::move(reference_zones));

  const auto buffer = ::dump::ToBinary(written_zones_cache);
  dump::MockReader reader(std::move(buffer));
  const auto read_zones_cache = reader.Read<models::DeliveryZonesCache>();
  reader.Finish();

  const auto& written_zones = written_zones_cache.GetZones();
  const auto& read_zones = read_zones_cache.GetZones();

  ASSERT_EQ(written_zones.size(), read_zones.size());
  for (std::size_t i = 0; i < written_zones.size(); ++i) {
    EnsureEqual(written_zones.at(i), read_zones.at(i));
  }
}
