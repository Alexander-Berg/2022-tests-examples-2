#include <gtest/gtest.h>

#include <models/geoarea.hpp>
#include <models/tariffs.hpp>
#include <models/zone_geoindex.hpp>

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

Geoarea::polygon_t MakePolygon(std::vector<Geoarea::point_t> points) {
  Geoarea::polygon_t res;
  for (auto&& point : std::move(points)) {
    boost::geometry::append(res, std::move(point));
  }
  return res;
}

std::pair<std::string, Geoarea::Sptr> MakeGeoarea(
    std::string name, const Geoarea::polygon_t& polygon, const double area) {
  Geoarea res(name, name, 0, polygon, area);
  return std::make_pair(std::move(name),
                        std::make_shared<Geoarea>(std::move(res)));
}

std::pair<std::string, tariff::Tariff> MakeTariff(std::string home_zone,
                                                  std::string activation_zone) {
  std::string key = home_zone;

  tariff::Tariff res;
  res.home_zone = std::move(home_zone);
  res.activation_zone = std::move(activation_zone);

  return std::make_pair(std::move(key), std::move(res));
}

namespace forward {

const Geoarea::geoarea_dict_t& GetGeoareas() {
  static const Geoarea::geoarea_dict_t geoareas{
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

const tariff::tariff_dict_t& GetTariffs() {
  static const tariff::tariff_dict_t tariffs_dict{
      MakeTariff(geoarea_name::kDefault, geoarea_name::kDefaultActivation),
      MakeTariff(geoarea_name::kSmall, geoarea_name::kSmallActivation),
      MakeTariff(geoarea_name::kMedium, geoarea_name::kMediumActivation),
      MakeTariff(geoarea_name::kBig, geoarea_name::kBigActivation)};
  return tariffs_dict;
}

}  // namespace forward

namespace backward {

const Geoarea::geoarea_dict_t& GetGeoareas() {
  static const Geoarea::geoarea_dict_t geoareas{
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

const tariff::tariff_dict_t& GetTariffs() {
  static const tariff::tariff_dict_t tariffs_dict{
      MakeTariff(geoarea_name::kSmall, geoarea_name::kSmallActivation),
      MakeTariff(geoarea_name::kBig, geoarea_name::kBigActivation)};
  return tariffs_dict;
}

}  // namespace backward

namespace simple {

const Geoarea::geoarea_dict_t& GetGeoareas() {
  static const Geoarea::geoarea_dict_t geoareas{
      // intersect
      MakeGeoarea(geoarea_name::kSmall,
                  MakePolygon({{-1, -1}, {-1, 1}, {1, 1}, {1, -1}, {-1, -1}}),
                  4),
      MakeGeoarea(geoarea_name::kBig,
                  MakePolygon({{-1, -3}, {-1, 3}, {3, 3}, {3, -3}, {-1, -3}}),
                  24),
      MakeGeoarea(geoarea_name::kSmallActivation,
                  MakePolygon({{-2, -2}, {-2, 2}, {2, 2}, {2, -2}, {-2, -2}}),
                  16),
      MakeGeoarea(geoarea_name::kBigActivation,
                  MakePolygon({{-2, -4}, {-2, 4}, {4, 4}, {4, -4}, {-2, -4}}),
                  48)};
  return geoareas;
}

const tariff::tariff_dict_t& GetTariffs() {
  static const tariff::tariff_dict_t tariffs_dict{
      MakeTariff(geoarea_name::kSmall, geoarea_name::kSmallActivation),
      MakeTariff(geoarea_name::kBig, geoarea_name::kBigActivation)};
  return tariffs_dict;
}

}  // namespace simple
}  // namespace

struct MatchZoneParam {
  const utils::geometry::Point point;
  const std::string matched_zone;
  const Geoarea::geoarea_dict_t& geoareas;
  const tariff::tariff_dict_t& tariffs;
  const models::ZoneGeoindex::VisibilityFilter filter;
};

class NearestZoneTest : public ::testing::TestWithParam<MatchZoneParam> {};

TEST_P(NearestZoneTest, NearestZoneTest) {
  const auto& [point, matched_zone, geoareas, tariffs, _] = GetParam();

  const models::ZoneGeoindex zone_geoindex{geoareas, tariffs};
  const auto res = zone_geoindex.FindNearest(point, {});
  EXPECT_EQ(res, matched_zone);
}

INSTANTIATE_TEST_CASE_P(NearestZoneTest, NearestZoneTest,
                        ::testing::Values(
                            // outside
                            MatchZoneParam{{7, 7},  // 0
                                           geoarea_name::kEmpty,
                                           ::forward::GetGeoareas(),
                                           ::forward::GetTariffs(),
                                           {}},
                            // inside home_zone
                            MatchZoneParam{{11, 11},  // 1
                                           geoarea_name::kDefault,
                                           ::forward::GetGeoareas(),
                                           ::forward::GetTariffs(),
                                           {}},
                            // inside activation_zone
                            MatchZoneParam{{9.5, 11},  // 2
                                           geoarea_name::kDefault,
                                           ::forward::GetGeoareas(),
                                           ::forward::GetTariffs(),
                                           {}},
                            // inside small
                            MatchZoneParam{{0, 0},  // 4
                                           geoarea_name::kSmall,
                                           ::forward::GetGeoareas(),
                                           ::forward::GetTariffs(),
                                           {}},
                            // inside two activations && inside one home
                            MatchZoneParam{{-0.5, 2.5},  // 5
                                           geoarea_name::kMedium,
                                           ::forward::GetGeoareas(),
                                           ::forward::GetTariffs(),
                                           {}},
                            // inside two activations && outside home
                            MatchZoneParam{{-1.1, 2.5},  // 6
                                           geoarea_name::kMedium,
                                           ::forward::GetGeoareas(),
                                           ::forward::GetTariffs(),
                                           {}},
                            MatchZoneParam{{-1.5, 2.1},  // 7
                                           geoarea_name::kMedium,
                                           ::forward::GetGeoareas(),
                                           ::forward::GetTariffs(),
                                           {}},
                            // activation.area less than another, but
                            // home.area is greater
                            MatchZoneParam{{0.5, 1.5},  // 8
                                           geoarea_name::kBig,
                                           ::backward::GetGeoareas(),
                                           ::backward::GetTariffs(),
                                           {}},
                            MatchZoneParam{{1.5, 0.5},  // 9
                                           geoarea_name::kSmall,
                                           ::backward::GetGeoareas(),
                                           ::backward::GetTariffs(),
                                           {}},
                            MatchZoneParam{
                                {0.00001, 0.99999},  // 10 (near {0.0, 1.0})
                                geoarea_name::kSmall,
                                ::backward::GetGeoareas(),
                                ::backward::GetTariffs(),
                                {}},
                            MatchZoneParam{{0.1, 0.9},  // 11
                                           geoarea_name::kSmall,
                                           ::backward::GetGeoareas(),
                                           ::backward::GetTariffs(),
                                           {}},
                            MatchZoneParam{{1.0, 0.0},  // 12
                                           geoarea_name::kSmall,
                                           ::backward::GetGeoareas(),
                                           ::backward::GetTariffs(),
                                           {}},
                            MatchZoneParam{{0.9, 0.1},  // 13
                                           geoarea_name::kSmall,
                                           ::backward::GetGeoareas(),
                                           ::backward::GetTariffs(),
                                           {}}  //
                            ), );

struct VisibilityFilter {
  VisibilityFilter(){};

  VisibilityFilter(const std::string& tariff_home_zone,
                   const std::unordered_set<std::string>& invisible_zones)
      : tariff_home_zone_(tariff_home_zone),
        invisible_zones_(invisible_zones) {}

  bool operator()(const std::string& zone, const tariff::Tariff& tariff) const {
    if (tariff.home_zone == tariff_home_zone_) {
      return (invisible_zones_.count(zone) == 0);
    }
    return true;
  }

 private:
  const std::string tariff_home_zone_;
  const std::unordered_set<std::string> invisible_zones_;
};

class VisibilityFilterTest : public ::testing::TestWithParam<MatchZoneParam> {};

TEST_P(VisibilityFilterTest, VisibilityFilterTest) {
  const auto& [point, matched_zone, geoareas, tariffs, filter] = GetParam();

  const models::ZoneGeoindex zone_geoindex{geoareas, tariffs};
  const auto res = zone_geoindex.FindNearest(point, filter, {});
  EXPECT_EQ(res, matched_zone);
}

INSTANTIATE_TEST_CASE_P(
    VisibilityFilterTest, VisibilityFilterTest,
    ::testing::Values(
        // no filter
        MatchZoneParam{{-1.5, 1.5},  // 0
                       geoarea_name::kSmall,
                       ::simple::GetGeoareas(),
                       ::simple::GetTariffs(),
                       VisibilityFilter{}},
        MatchZoneParam{{-1.5, 2.5},  // 1
                       geoarea_name::kBig,
                       ::simple::GetGeoareas(),
                       ::simple::GetTariffs(),
                       VisibilityFilter{}},
        // match kSmall inside kBig, but filter it as invisible
        MatchZoneParam{
            {-1.5, 1.5},  // 2
            geoarea_name::kEmpty,
            ::simple::GetGeoareas(),
            ::simple::GetTariffs(),
            VisibilityFilter{geoarea_name::kSmall, {geoarea_name::kSmall}}},
        // match kBig, but filter it as invisible
        MatchZoneParam{
            {-1.5, 2.5},  // 3
            geoarea_name::kEmpty,
            ::simple::GetGeoareas(),
            ::simple::GetTariffs(),
            VisibilityFilter{geoarea_name::kBig, {geoarea_name::kBig}}}  //
        ), );
