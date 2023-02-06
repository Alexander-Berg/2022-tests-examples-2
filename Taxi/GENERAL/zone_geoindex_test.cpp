#include <gtest/gtest.h>

#include <boost/range/adaptor/transformed.hpp>

#include <client-zone-geoindex/models/zone_geoindex.hpp>

#include <set>

namespace {
namespace geoarea_name {

const std::string kEmpty{};

const std::string kDefault{"default"};
const std::string kDefaultActivation{"default_activation"};

const std::string kSmall{"small"};
const std::string kSmallActivation{"small_activation"};
const std::string kMedium{"medium"};
const std::string kMediumActivation{"medium_activation"};
const std::string kBig{"big"};
const std::string kBigActivation{"big_activation"};

}  // namespace geoarea_name

namespace czgi = client_zone_geoindex::models;

czgi::Geoarea::Polygon MakePolygon(std::vector<czgi::Geoarea::Point> points) {
  czgi::Geoarea::Polygon res;
  for (auto&& point : std::move(points)) {
    boost::geometry::append(res, std::move(point));
  }
  return res;
}

std::pair<std::string, czgi::GeoareaPtr> MakeGeoarea(
    std::string name, const czgi::Geoarea::Polygon& polygon,
    const double area) {
  czgi::Geoarea res(name, polygon, area, {});
  return std::make_pair(std::move(name),
                        std::make_shared<czgi::Geoarea>(std::move(res)));
}

std::pair<std::string, czgi::Tariff> MakeTariff(std::string home_zone,
                                                std::string activation_zone) {
  std::string key = home_zone;

  czgi::Tariff res;
  res.home_zone = std::move(home_zone);
  res.activation_zone = std::move(activation_zone);

  return std::make_pair(std::move(key), std::move(res));
}

namespace forward {

const czgi::Geoareas& GetGeoareas() {
  static const czgi::Geoareas geoareas{
      MakeGeoarea(
          "not_tariff_zone",
          MakePolygon({{-10, -10}, {-10, 10}, {10, 10}, {10, -10}, {-10, -10}}),
          400),
      // simple
      MakeGeoarea(
          geoarea_name::kDefault,
          MakePolygon({{10, 10}, {10, 12}, {12, 12}, {12, 10}, {10, 10}}), 4),
      MakeGeoarea(geoarea_name::kDefaultActivation,
                  MakePolygon({{9, 9}, {9, 13}, {13, 13}, {13, 9}, {9, 9}}),
                  16),
      // intersect
      MakeGeoarea(geoarea_name::kSmall,
                  MakePolygon({{-1, -1}, {-1, 1}, {1, 1}, {1, -1}, {-1, -1}}),
                  4),
      MakeGeoarea(geoarea_name::kMedium,
                  MakePolygon({{-2, -2}, {-2, 2}, {0, 2}, {0, -2}, {-2, -2}}),
                  8),
      MakeGeoarea(geoarea_name::kBig,
                  MakePolygon({{-1, -3}, {-1, 3}, {3, 3}, {3, -3}, {-1, -3}}),
                  24),
      MakeGeoarea(geoarea_name::kSmallActivation,
                  MakePolygon({{-2, -2}, {-2, 2}, {2, 2}, {2, -2}, {-2, -2}}),
                  16),
      MakeGeoarea(geoarea_name::kMediumActivation,
                  MakePolygon({{-3, -3}, {-3, 3}, {1, 3}, {1, -3}, {-3, -3}}),
                  24),
      MakeGeoarea(geoarea_name::kBigActivation,
                  MakePolygon({{-2, -4}, {-2, 4}, {4, 4}, {4, -4}, {-2, -4}}),
                  48)};
  return geoareas;
}

const czgi::Tariffs& GetTariffs() {
  static const czgi::Tariffs tariffs_dict{
      MakeTariff(geoarea_name::kDefault, geoarea_name::kDefaultActivation),
      MakeTariff(geoarea_name::kSmall, geoarea_name::kSmallActivation),
      MakeTariff(geoarea_name::kMedium, geoarea_name::kMediumActivation),
      MakeTariff(geoarea_name::kBig, geoarea_name::kBigActivation)};
  return tariffs_dict;
}

}  // namespace forward

namespace backward {

const czgi::Geoareas& GetGeoareas() {
  static const czgi::Geoareas geoareas{
      // intersect
      MakeGeoarea(geoarea_name::kSmallActivation,
                  MakePolygon({{0, -2}, {0, 1}, {2, 1}, {2, -2}, {0, -2}}), 6),
      MakeGeoarea(geoarea_name::kBigActivation,
                  MakePolygon({{-3, 0}, {-3, 2}, {1, 2}, {1, 0}, {-3, 0}}), 8),
      MakeGeoarea(geoarea_name::kSmall,
                  MakePolygon({{0.1, -1.9},
                               {0.1, -0.2},
                               {1.9, -0.2},
                               {1.9, -1.9},
                               {0.1, -1.9}}),
                  3.06),
      MakeGeoarea(geoarea_name::kBig,
                  MakePolygon({{-1.0, 0.1},
                               {-1.0, 1.9},
                               {-0.1, 1.9},
                               {-0.1, 0.1},
                               {-1.0, 0.1}}),
                  1.62)};
  return geoareas;
}

const czgi::Tariffs& GetTariffs() {
  static const czgi::Tariffs tariffs_dict{
      MakeTariff(geoarea_name::kSmall, geoarea_name::kSmallActivation),
      MakeTariff(geoarea_name::kBig, geoarea_name::kBigActivation)};
  return tariffs_dict;
}

}  // namespace backward
}  // namespace

struct MatchZoneParam {
  const ::models::geometry::Point point;
  const std::string matched_zone;
  const czgi::Geoareas& geoareas;
  const czgi::Tariffs& tariffs;
};

class NearestZoneTest : public ::testing::TestWithParam<MatchZoneParam> {};

TEST_P(NearestZoneTest, Test) {
  const auto& [point, matched_zone, geoareas, tariffs] = GetParam();

  czgi::ZoneGeoindex zone_geo_index(geoareas, tariffs);
  const auto res = zone_geo_index.MatchNearest(point);

  EXPECT_EQ((res ? res->name() : geoarea_name::kEmpty), matched_zone);
}

INSTANTIATE_TEST_SUITE_P(NearestZoneTest, NearestZoneTest,
                         ::testing::Values(
                             // outside
                             MatchZoneParam{{7, 7},  // 0
                                            geoarea_name::kEmpty,
                                            ::forward::GetGeoareas(),
                                            ::forward::GetTariffs()},
                             // inside home_zone
                             MatchZoneParam{{11, 11},  // 1
                                            geoarea_name::kDefault,
                                            ::forward::GetGeoareas(),
                                            ::forward::GetTariffs()},
                             // inside activation_zone
                             MatchZoneParam{{9.5, 11},  // 2
                                            geoarea_name::kDefault,
                                            ::forward::GetGeoareas(),
                                            ::forward::GetTariffs()},
                             // inside small
                             MatchZoneParam{{0, 0},  // 3
                                            geoarea_name::kSmall,
                                            ::forward::GetGeoareas(),
                                            ::forward::GetTariffs()},
                             // inside two activations && inside one home
                             MatchZoneParam{{-0.5, 2.5},  // 4
                                            geoarea_name::kMedium,
                                            ::forward::GetGeoareas(),
                                            ::forward::GetTariffs()},
                             // inside two activations && outside home
                             MatchZoneParam{{-1.1, 2.5},  // 5
                                            geoarea_name::kMedium,
                                            ::forward::GetGeoareas(),
                                            ::forward::GetTariffs()},
                             MatchZoneParam{{-1.5, 2.1},  // 6
                                            geoarea_name::kMedium,
                                            ::forward::GetGeoareas(),
                                            ::forward::GetTariffs()},
                             // activation.area less than another, but
                             // home.area is greater
                             MatchZoneParam{{0.5, 1.5},  // 7
                                            geoarea_name::kBig,
                                            ::backward::GetGeoareas(),
                                            ::backward::GetTariffs()},
                             MatchZoneParam{{1.5, 0.5},  // 8
                                            geoarea_name::kSmall,
                                            ::backward::GetGeoareas(),
                                            ::backward::GetTariffs()},
                             MatchZoneParam{
                                 {0.00001, 0.99999},  // 9 (near of {0.0, 1.0})
                                 geoarea_name::kSmall,
                                 ::backward::GetGeoareas(),
                                 ::backward::GetTariffs()},
                             MatchZoneParam{{0.1, 0.9},  // 10
                                            geoarea_name::kSmall,
                                            ::backward::GetGeoareas(),
                                            ::backward::GetTariffs()},
                             MatchZoneParam{{1.0, 0.0},  // 11
                                            geoarea_name::kSmall,
                                            ::backward::GetGeoareas(),
                                            ::backward::GetTariffs()},
                             MatchZoneParam{{0.9, 0.1},  // 12
                                            geoarea_name::kSmall,
                                            ::backward::GetGeoareas(),
                                            ::backward::GetTariffs()}  //
                             ));

template <typename T, typename R>
T As(const R& range) {
  return T(range.begin(), range.end());
}

struct MatchZoneInRadiusParam {
  const ::models::geometry::Point point;
  const int radius;
  const std::set<std::string> matched_zones;
  const czgi::Geoareas& geoareas;
  const czgi::Tariffs& tariffs;
};

class NearestZoneInRadiusTest
    : public ::testing::TestWithParam<MatchZoneInRadiusParam> {};

TEST_P(NearestZoneInRadiusTest, Test) {
  const auto& [point, radius, matched_zones, geoareas, tariffs] = GetParam();

  czgi::ZoneGeoindex zone_geo_index(geoareas, tariffs);
  const auto res = zone_geo_index.MatchInRadius(point, radius);

  EXPECT_EQ(As<std::set<std::string>>(
                res | boost::adaptors::transformed(
                          [](const auto& zone) { return zone->name(); })),
            matched_zones);
}

INSTANTIATE_TEST_SUITE_P(NearestZoneInRadiusTest, NearestZoneInRadiusTest,
                         ::testing::Values(
                             // outside
                             MatchZoneInRadiusParam{
                                 {7, 7},  // 0
                                 10,
                                 {},
                                 ::forward::GetGeoareas(),
                                 ::forward::GetTariffs(),
                             },
                             // inside home_zone
                             MatchZoneInRadiusParam{
                                 {11, 11},  // 1
                                 500000,
                                 {geoarea_name::kDefault},
                                 ::forward::GetGeoareas(),
                                 ::forward::GetTariffs(),
                             },
                             // inside home_zone, 1000km radius
                             MatchZoneInRadiusParam{
                                 {11, 11},  // 2
                                 1000000,
                                 {geoarea_name::kDefault, geoarea_name::kBig,
                                  geoarea_name::kSmall},
                                 ::forward::GetGeoareas(),
                                 ::forward::GetTariffs(),
                             }));
