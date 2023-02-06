#include <vector>

#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>
#include <userver/formats/json.hpp>
#include <userver/utils/datetime.hpp>

#include <geometry/position_as_array.hpp>

#include <models/dispatch-airport/zones_geo_index.hpp>
#include <models/geometry/distance.hpp>

namespace formats::parse {

static client_geoareas::models::Geoarea::point_t Parse(
    const formats::json::Value& doc,
    formats::parse::To<client_geoareas::models::Geoarea::point_t>) {
  return client_geoareas::models::Geoarea::point_t{doc[0].As<double>(),
                                                   doc[1].As<double>()};
}

static client_geoareas::models::Geoarea::polygon_t Parse(
    const formats::json::Value& doc,
    formats::parse::To<client_geoareas::models::Geoarea::polygon_t>) {
  client_geoareas::models::Geoarea::polygon_t polygon;
  for (const auto& point_doc : doc) {
    boost::geometry::append(
        polygon, point_doc.As<client_geoareas::models::Geoarea::point_t>());
  }
  return polygon;
}

}  // namespace formats::parse

namespace {

using Zone = models::dispatch::airport::Zone;
using ZoneTypes = std::unordered_map<std::string, Zone::DistributiveZoneType>;

formats::json::Value LoadJson(const std::string& fname) {
  static const std::string path(utils::CurrentSourcePath("src/tests/static/"));
  return formats::json::blocking::FromFile(path + fname);
}

std::shared_ptr<client_geoareas::models::Geoarea> FromJson(
    formats::json::Value doc) {
  std::vector<std::vector<geometry::Position>> positions;
  std::string id_ = doc["_id"].As<std::string>();
  std::string name_ = doc["name"].As<std::string>();
  std::chrono::system_clock::time_point created_ =
      utils::datetime::Stringtime(doc["created"].As<std::string>());
  client_geoareas::models::Polygon polygon_ =
      doc["geometry"]["coordinates"][0].As<client_geoareas::models::Polygon>();

  std::vector<std::vector<geometry::Position>> positions_(1);

  positions_[0].reserve(polygon_.outer().size());
  for (auto& vertex : polygon_.outer()) {
    using boost::geometry::get;
    positions_[0].push_back(geometry::Position(get<0>(vertex) * geometry::lat,
                                               get<1>(vertex) * geometry::lon));
  }

  return std::make_shared<client_geoareas::models::Geoarea>(
      std::move(id_), /*type=*/std::string(), std::move(name_), created_,
      positions_,
      std::unordered_set<client_geoareas::models::Geoarea::ZoneType>(),
      std::nullopt);
}

client_geoareas::models::Geoarea::geoarea_dict_t LoadGeoareas() {
  const auto js_areas = LoadJson("geoareas.json");

  client_geoareas::models::Geoarea::geoarea_dict_t ret;
  for (auto& js_area : js_areas) {
    auto geoarea = FromJson(js_area);
    std::string name = geoarea->name();
    ret.emplace(std::move(name), geoarea);
  }

  return ret;
}

std::vector<Zone> LoadAirportZones(
    const client_geoareas::models::Geoarea::geoarea_dict_t& geoareas,
    const ZoneTypes& zone_types = {},
    const std::string& airport_zones_filename = "airport_zones.json") {
  std::vector<Zone> ret;

  constexpr bool pin_info_enabled = true;

  const auto& js_zones = LoadJson(airport_zones_filename);
  ret.reserve(js_zones.GetSize());
  for (const auto& js_zone : js_zones) {
    const auto zone_name = js_zone["name"].As<std::string>();

    std::optional<Zone::DistributiveZoneType> distributive_zone_type;
    const auto it = zone_types.find(zone_name);
    if (it != zone_types.end()) {
      distributive_zone_type = it->second;
    }

    ret.emplace_back(zone_name, *geoareas.at(js_zone["main"].As<std::string>()),
                     *geoareas.at(js_zone["waiting"].As<std::string>()),
                     *geoareas.at(js_zone["notification"].As<std::string>()),
                     js_zone["is_used"].As<bool>(), pin_info_enabled,
                     distributive_zone_type);
  }

  return ret;
}

std::vector<std::string> GetPinZones(
    const std::vector<std::reference_wrapper<const Zone>>& found_zones) {
  std::vector<std::string> zone_names;
  for (const auto& zone : found_zones) {
    zone_names.push_back(zone.get().GetName());
  }
  std::sort(zone_names.begin(), zone_names.end());

  return zone_names;
}

UTEST(DispatchAirport, ZonesIndexFindZones) {
  using AreaType = models::dispatch::airport::Zone::AreaType;
  using AreaTypes = models::dispatch::airport::ZonesGeoIndex::AreaTypes;
  const auto all_zones =
      AreaTypes::Make<AreaType::kMain, AreaType::kNotification,
                      AreaType::kWaiting>();

  auto geoareas = LoadGeoareas();
  auto zones = LoadAirportZones(geoareas);
  auto geo_index = models::dispatch::airport::ZonesGeoIndex(zones);

  // point inside both zones
  auto found_zones = geo_index.FindZones(
      models::dispatch::airport::Geoarea::point_t(43.5, 133.5));
  std::sort(found_zones.begin(), found_zones.end(),
            [](const auto& lhs, const auto& rhs) {
              return lhs.zone->GetName() < rhs.zone->GetName();
            });
  ASSERT_EQ(found_zones.size(), 2);
  ASSERT_EQ(found_zones[0].zone->GetName(), "artem_airport");
  ASSERT_EQ(found_zones[0].matched_zones, all_zones);
  ASSERT_EQ(found_zones[1].zone->GetName(), "bigger_artem_airport");
  ASSERT_EQ(found_zones[1].matched_zones, all_zones);

  // point outside both zones
  auto found_zones2 =
      geo_index.FindZones(models::dispatch::airport::Geoarea::point_t(46, 138));
  ASSERT_EQ(found_zones2.size(), 0);

  // point inside one zone
  auto found_zones3 = geo_index.FindZones(
      models::dispatch::airport::Geoarea::point_t(44.5, 134.5));
  ASSERT_EQ(found_zones3.size(), 1);
  ASSERT_EQ(found_zones3[0].zone->GetName(), "bigger_artem_airport");
  const auto found_zones3_match_etalon =
      AreaTypes::Make<AreaType::kNotification, AreaType::kWaiting>();
  ASSERT_EQ(found_zones3[0].matched_zones, found_zones3_match_etalon);
}

UTEST(DispatchAirport, ZonesIndexFindActivePinZones) {
  using AreaType = models::dispatch::airport::Zone::AreaType;
  using AreaTypes = models::dispatch::airport::ZonesGeoIndex::AreaTypes;
  using PinAirportSettings =
      models::dispatch::airport::ZonesGeoIndex::PinAirportSettings;
  using PinsAirportsSettings =
      models::dispatch::airport::ZonesGeoIndex::PinsAirportsSettings;
  const auto area_types = AreaTypes::Make<AreaType::kWaiting>();

  auto geoareas = LoadGeoareas();
  auto zones = LoadAirportZones(geoareas);
  auto geo_index = models::dispatch::airport::ZonesGeoIndex(zones);

  uint32_t degree_in_meters = models::geometry::LatDegreeLength(43.5);
  // inside far_artem_airport, radius < dist(point, other airports)
  PinAirportSettings default_airport_settings{1, std::nullopt, false};
  auto found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 140.5}, default_airport_settings));
  ASSERT_EQ(found_zones.size(), 0);
  // inside far_artem_airport, radius > dist(point, other airports)
  default_airport_settings.radius_m = 7 * degree_in_meters;
  found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 140.5}, default_airport_settings));
  ASSERT_EQ(found_zones.size(), 2);
  ASSERT_EQ(found_zones[0], "artem_airport");
  ASSERT_EQ(found_zones[1], "bigger_artem_airport");

  // outside all airports, bigger and far airports in radius
  default_airport_settings.radius_m = 4 * degree_in_meters;
  found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 138.5}, default_airport_settings));
  ASSERT_EQ(found_zones.size(), 2);
  ASSERT_EQ(found_zones[0], "bigger_artem_airport");
  ASSERT_EQ(found_zones[1], "far_artem_airport");

  // outside all airports, bigger and far airports in global radius
  // but far airport has redefined radius < dist
  PinsAirportsSettings specific_airport_settings{
      {"far_artem_airport",
       PinAirportSettings{degree_in_meters, std::nullopt, false}}};
  found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 138.5}, default_airport_settings,
      area_types, specific_airport_settings));
  ASSERT_EQ(found_zones.size(), 1);
  ASSERT_EQ(found_zones[0], "bigger_artem_airport");

  // outside all airports, bigger and far airports in far_airport_radius
  // but global_radius < dist(point, bigger_airport_radius)
  default_airport_settings.radius_m = degree_in_meters;
  specific_airport_settings = PinsAirportsSettings{
      {"far_artem_airport",
       PinAirportSettings{3 * degree_in_meters, std::nullopt, false}}};

  found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 138.5}, default_airport_settings,
      area_types, specific_airport_settings));
  ASSERT_EQ(found_zones.size(), 1);
  ASSERT_EQ(found_zones[0], "far_artem_airport");

  // inside far_artem_airport, but enabled in airport by default
  // radius < dist(point, other airports)
  default_airport_settings.radius_m = 1;
  default_airport_settings.enabled_in_airport = true;
  found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 140.5}, default_airport_settings));
  ASSERT_EQ(found_zones.size(), 1);
  ASSERT_EQ(found_zones[0], "far_artem_airport");

  // inside far_artem_airport, but enabled in specific airport
  // radius < dist(point, other airports)
  default_airport_settings.enabled_in_airport = false;
  specific_airport_settings = PinsAirportsSettings{
      {"far_artem_airport", PinAirportSettings{1, std::nullopt, true}}};
  found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 140.5}, default_airport_settings,
      area_types, specific_airport_settings));
  ASSERT_EQ(found_zones.size(), 1);
  ASSERT_EQ(found_zones[0], "far_artem_airport");

  // inside far_artem_airport, enabled in airport by default, but disabled by
  // min_radius_m radius < dist(point, other airports)
  default_airport_settings.enabled_in_airport = true;
  default_airport_settings.min_radius_m = 1000;
  found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 140.5}, default_airport_settings));
  ASSERT_EQ(found_zones.size(), 0);

  // inside far_artem_airport, enabled in specifg airport by, but disabled by
  // min_radius_m radius < dist(point, other airports)
  default_airport_settings.enabled_in_airport = false;
  default_airport_settings.min_radius_m = std::nullopt;
  specific_airport_settings = PinsAirportsSettings{
      {"far_artem_airport", PinAirportSettings{1, 1000, true}}};
  found_zones = GetPinZones(geo_index.FindActivePinZones(
      ::models::geometry::Point{43.5, 140.5}, default_airport_settings,
      area_types, specific_airport_settings));
  ASSERT_EQ(found_zones.size(), 0);
}

UTEST(DispatchAirport, ZonesIndexFindByPointMatchAreaType) {
  auto geoareas = LoadGeoareas();
  auto zones = LoadAirportZones(
      geoareas, {}, "airport_zones_find_by_point_match_area_type.json");
  auto geo_index = models::dispatch::airport::ZonesGeoIndex(zones);

  // point inside both airports, but only inside bigger_artem_airport main area
  auto found_zone =
      geo_index(models::dispatch::airport::Geoarea::point_t(44.5, 134.5));
  ASSERT_EQ(found_zone.zone->GetName(), "bigger_artem_airport");
}

UTEST(DispatchAirport, ZonesIndexFindByPointUsedFlagDiffers) {
  auto geoareas = LoadGeoareas();
  auto zones = LoadAirportZones(
      geoareas, {}, "airport_zones_find_by_point_used_flag_differs.json");
  auto geo_index = models::dispatch::airport::ZonesGeoIndex(zones);

  // point inside both zones
  auto found_zone =
      geo_index(models::dispatch::airport::Geoarea::point_t(43.5, 133.5));
  ASSERT_EQ(found_zone.zone->GetName(), "bigger_artem_airport");
}

class ZonesIndexFindByPoint
    : public ::testing::TestWithParam<std::tuple<
          std::unordered_map<std::string, Zone::DistributiveZoneType>,
          std::string>> {};

TEST_P(ZonesIndexFindByPoint, ZonesIndexFindByPoint) {
  const auto& [zone_types, expected_airport] = GetParam();

  auto geoareas = LoadGeoareas();
  auto zones = LoadAirportZones(geoareas, zone_types);
  auto geo_index = models::dispatch::airport::ZonesGeoIndex(zones);

  // point inside both zones
  auto found_zone =
      geo_index(models::dispatch::airport::Geoarea::point_t(43.5, 133.5));
  ASSERT_EQ(found_zone.zone->GetName(), expected_airport);
}

INSTANTIATE_TEST_SUITE_P(
    ZonesIndexFindByPoint, ZonesIndexFindByPoint,
    ::testing::Values(
        // case 1: select by alphabetical order
        std::make_tuple(ZoneTypes{}, "artem_airport"),
        // case 2: select by alphabetical order, waiting type doesn't matter
        std::make_tuple(ZoneTypes{{"artem_airport",
                                   Zone::DistributiveZoneType::kWaiting}},
                        "artem_airport"),
        // case 3: select non check-in airport
        std::make_tuple(ZoneTypes{{"artem_airport",
                                   Zone::DistributiveZoneType::kCheckIn}},
                        "bigger_artem_airport"),
        // case 4: select non distributive airport
        std::make_tuple(ZoneTypes{{"artem_airport",
                                   Zone::DistributiveZoneType::kDistributive}},
                        "bigger_artem_airport"),
        // case 5: prefer check-in over distributive
        std::make_tuple(ZoneTypes{{"artem_airport",
                                   Zone::DistributiveZoneType::kDistributive},
                                  {"bigger_artem_airport",
                                   Zone::DistributiveZoneType::kCheckIn}},
                        "bigger_artem_airport")));

}  // namespace
