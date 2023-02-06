#include <gmock/gmock-matchers.h>
#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <models/route_variant.hpp>

using RoutePoint = combo_contractors::models::RoutePoint;
using Type = combo_contractors::models::RoutePointType;
using RouteVariant = combo_contractors::models::RouteVariant;

namespace combo_contractors::models {

bool operator<(const RoutePoint& a, const RoutePoint& b) {
  return std::tie(a.order_id, a.type) < std::tie(b.order_id, b.type);
}

}  // namespace combo_contractors::models

namespace {

void DoTest(const std::vector<RoutePoint>& contractor_route,
            const std::vector<RoutePoint>& order_route,
            bool match_start_RoutePoints_ordered, bool need_only_nested,
            const std::vector<RouteVariant>& expected_variants) {
  auto variants = combo_contractors::models::BuildRouteVariants(
      contractor_route, order_route, match_start_RoutePoints_ordered,
      need_only_nested);

  std::sort(variants.begin(), variants.end(),
            [](const auto& a, const auto& b) { return a.route < b.route; });

  std::vector<testing::Matcher<RouteVariant>> matchers;

  for (const auto& variant : expected_variants) {
    matchers.push_back(
        testing::AllOf(testing::Field("route", &RouteVariant::route,
                                      testing::ElementsAreArray(variant.route)),
                       testing::Field("is_nested", &RouteVariant::is_nested,
                                      variant.is_nested)));
  }

  ASSERT_THAT(variants, testing::ElementsAreArray(matchers));
}

}  // namespace

TEST(BuildRouteVariants, MatchInTransporting) {
  std::vector<RoutePoint> contractor_route{{"id0", Type::kStart, {}, {}},
                                           {"id0", Type::kContractor, {}, {}},
                                           {"id0", Type::kFinish, {}, {}}};

  std::vector<RoutePoint> order_route{{"id1", Type::kStart, {}, {}},
                                      {"id1", Type::kFinish, {}, {}}};

  std::vector<RouteVariant> expected_variants{
      {{{"id0", Type::kStart, {}, {}},
        {"id0", Type::kContractor, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id0", Type::kFinish, {}, {}},
        {"id1", Type::kFinish, {}, {}}},
       false,
       false /*is_nested*/,
       0,
       {},
       {},
       {}},
      {{{"id0", Type::kStart, {}, {}},
        {"id0", Type::kContractor, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id1", Type::kFinish, {}, {}},
        {"id0", Type::kFinish, {}, {}}},
       false,
       true /*is_nested*/,
       0,
       {},
       {},
       {}}};

  DoTest(contractor_route, order_route, false, false, expected_variants);
}

TEST(BuildRouteVariants, MatchInTransportingOnlyNested) {
  std::vector<RoutePoint> contractor_route{{"id0", Type::kStart, {}, {}},
                                           {"id0", Type::kContractor, {}, {}},
                                           {"id0", Type::kFinish, {}, {}}};

  std::vector<RoutePoint> order_route{{"id1", Type::kStart, {}, {}},
                                      {"id1", Type::kFinish, {}, {}}};

  std::vector<RouteVariant> expected_variants{
      {{{"id0", Type::kStart, {}, {}},
        {"id0", Type::kContractor, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id1", Type::kFinish, {}, {}},
        {"id0", Type::kFinish, {}, {}}},
       false,
       true /*is_nested*/,
       0,
       {},
       {},
       {}}};

  DoTest(contractor_route, order_route, false, true, expected_variants);
}

TEST(BuildRouteVariants, MatchInDriving) {
  std::vector<RoutePoint> contractor_route{{"id0", Type::kContractor, {}, {}},
                                           {"id0", Type::kStart, {}, {}},
                                           {"id0", Type::kFinish, {}, {}}};

  std::vector<RoutePoint> order_route{{"id1", Type::kStart, {}, {}},
                                      {"id1", Type::kFinish, {}, {}}};

  std::vector<RouteVariant> expected_variants{
      {{{"id0", Type::kContractor, {}, {}},
        {"id0", Type::kStart, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id0", Type::kFinish, {}, {}},
        {"id1", Type::kFinish, {}, {}}},
       false,
       false /*is_nested*/,
       0,
       {},
       {},
       {}},
      {{{"id0", Type::kContractor, {}, {}},
        {"id0", Type::kStart, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id1", Type::kFinish, {}, {}},
        {"id0", Type::kFinish, {}, {}}},
       false,
       true /*is_nested*/,
       0,
       {},
       {},
       {}},
      {{{"id0", Type::kContractor, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id0", Type::kStart, {}, {}},
        {"id0", Type::kFinish, {}, {}},
        {"id1", Type::kFinish, {}, {}}},
       false,
       false /*is_nested*/,
       0,
       {},
       {},
       {}},
      {{{"id0", Type::kContractor, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id0", Type::kStart, {}, {}},
        {"id1", Type::kFinish, {}, {}},
        {"id0", Type::kFinish, {}, {}}},
       false,
       false /*is_nested*/,
       0,
       {},
       {},
       {}},

  };

  DoTest(contractor_route, order_route, false, false, expected_variants);
}

TEST(BuildRouteVariants, MatchInDrivingStartRoutePointsOrdered) {
  std::vector<RoutePoint> contractor_route{{"id0", Type::kContractor, {}, {}},
                                           {"id0", Type::kStart, {}, {}},
                                           {"id0", Type::kFinish, {}, {}}};

  std::vector<RoutePoint> order_route{{"id1", Type::kStart, {}, {}},
                                      {"id1", Type::kFinish, {}, {}}};

  std::vector<RouteVariant> expected_variants{
      {{{"id0", Type::kContractor, {}, {}},
        {"id0", Type::kStart, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id0", Type::kFinish, {}, {}},
        {"id1", Type::kFinish, {}, {}}},
       false,
       false /*is_nested*/,
       0,
       {},
       {},
       {}},
      {{{"id0", Type::kContractor, {}, {}},
        {"id0", Type::kStart, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id1", Type::kFinish, {}, {}},
        {"id0", Type::kFinish, {}, {}}},
       false,
       true /*is_nested*/,
       0,
       {},
       {},
       {}}};

  DoTest(contractor_route, order_route, true, false, expected_variants);
}

TEST(BuildRouteVariants, MatchInDrivingStartRoutePointsOrderedOnlyNested) {
  std::vector<RoutePoint> contractor_route{{"id0", Type::kContractor, {}, {}},
                                           {"id0", Type::kStart, {}, {}},
                                           {"id0", Type::kFinish, {}, {}}};

  std::vector<RoutePoint> order_route{{"id1", Type::kStart, {}, {}},
                                      {"id1", Type::kFinish, {}, {}}};

  std::vector<RouteVariant> expected_variants{
      {{{"id0", Type::kContractor, {}, {}},
        {"id0", Type::kStart, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id1", Type::kFinish, {}, {}},
        {"id0", Type::kFinish, {}, {}}},
       false,
       true /*is_nested*/,
       0,
       {},
       {},
       {}}};

  DoTest(contractor_route, order_route, true, true, expected_variants);
}

TEST(BuildRouteVariants, MatchInDrivingOnlyNested) {
  std::vector<RoutePoint> contractor_route{{"id0", Type::kContractor, {}, {}},
                                           {"id0", Type::kStart, {}, {}},
                                           {"id0", Type::kFinish, {}, {}}};

  std::vector<RoutePoint> order_route{{"id1", Type::kStart, {}, {}},
                                      {"id1", Type::kFinish, {}, {}}};

  std::vector<RouteVariant> expected_variants{
      {{{"id0", Type::kContractor, {}, {}},
        {"id0", Type::kStart, {}, {}},
        {"id1", Type::kStart, {}, {}},
        {"id1", Type::kFinish, {}, {}},
        {"id0", Type::kFinish, {}, {}}},
       false,
       true /*is_nested*/,
       0,
       {},
       {},
       {}}};

  DoTest(contractor_route, order_route, false, true, expected_variants);
}
