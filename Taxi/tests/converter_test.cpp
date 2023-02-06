#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

#include <userver/fs/blocking/read.hpp>

#include <userver/formats/json/serialize.hpp>

#include <helpers/converters.hpp>
#include <models/pg/geooffer_zones.hpp>

using namespace grocery_delivery_conditions::helpers;

namespace {

formats::json::Value LoadJson(const std::string& file_name) {
  auto contents = fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("src/tests/static/" + file_name));
  return formats::json::FromString(contents);
}

static const std::chrono::system_clock::time_point updated =
    ::utils::datetime::Stringtime("2020-08-01T22:10:00Z", "UTC");

static const std::string kZoneId = "zone_id";
static const std::string kZoneType = "zone_type";

}  // namespace

TEST(Converters, ConvertGeoOfferZoneGeometry) {
  grocery_delivery_conditions::models::pg::GeoOfferZoneRaw zone_raw;

  zone_raw.zone_id = kZoneId;
  zone_raw.zone_type = kZoneType;
  zone_raw.zone_geojson = LoadJson("geometry_info.json");
  zone_raw.status =
      grocery_delivery_conditions::models::GeoOfferZoneStatus::kActive;
  zone_raw.updated = updated;
  zone_raw.created = updated;

  const auto result = Convert(
      zone_raw, To<grocery_delivery_conditions::models::GeoOfferZone>());

  ASSERT_EQ(result.zone_id, kZoneId);
  ASSERT_EQ(result.zone_type, kZoneType);
  ASSERT_EQ(result.geometry.outer().size(), 9);
  ASSERT_EQ(result.geometry.inners().size(), 0);
  ASSERT_EQ(result.geometry.outer()[0].longitude,
            geometry::Longitude{30.301934});
  ASSERT_EQ(result.geometry.outer()[0].latitude, geometry::Latitude{59.898485});
  ASSERT_EQ(result.geometry.outer()[7].longitude,
            geometry::Longitude{30.301386});
  ASSERT_EQ(result.geometry.outer()[7].latitude, geometry::Latitude{59.898442});
  ASSERT_EQ(result.status,
            grocery_delivery_conditions::models::GeoOfferZoneStatus::kActive);
  ASSERT_EQ(result.updated, updated);
  ASSERT_EQ(result.created, updated);
}
