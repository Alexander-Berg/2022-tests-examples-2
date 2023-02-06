#include <gmock/gmock-matchers.h>
#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <chrono>
#include <unordered_map>

#include <userver/utest/utest.hpp>

#include <clients/routing/router_types.hpp>
#include <geometry/position.hpp>
#include <geometry/units.hpp>
#include <math-expr/math-expr.hpp>
#include <order-access/models/order_statuses.hpp>

#include <components/routing.hpp>
#include <components/routing_cache.hpp>
#include <models/contractor_orders.hpp>
#include <models/match_helper.hpp>
#include <models/order_ready_status.hpp>
#include <models/order_route_info.hpp>
#include <models/route_point.hpp>
#include <models/route_point_serialization.hpp>
#include <models/route_variant_serialization.hpp>

namespace {

namespace cm = combo_contractors::models;
namespace cc = combo_contractors::components;

using namespace std::chrono_literals;

using geometry::lat;
using geometry::lon;

using Position = geometry::Position;
using TimePoint = std::chrono::system_clock::time_point;
using PointType = cm::RoutePointType;

const Position kContractorPosition{4 * lon, 0 * lat};

const cm::RoutePoint kContractorPoint{
    "", PointType::kContractor, kContractorPosition, {}};

const std::vector<std::vector<cm::RoutePoint>> kPoints{
    {{"order_id0", PointType::kStart, Position{0 * lon, 0 * lat},
      TimePoint{0s}},
     {"order_id0", PointType::kFinish, Position{1 * lon, 0 * lat},
      TimePoint{1s}}},
    {{"order_id1", PointType::kStart, Position{2 * lon, 0 * lat},
      TimePoint{2s}},
     {"order_id1", PointType::kFinish, Position{8 * lon, 0 * lat}, {}}},
    {{"order_id2", PointType::kStart, Position{3 * lon, 0 * lat},
      TimePoint{3s}},
     {"order_id2", PointType::kFinish, Position{7 * lon, 0 * lat}, {}}},
    {{"order_id3", PointType::kStart, Position{5 * lon, 0 * lat}, {}},
     {"order_id3", PointType::kFinish, Position{6 * lon, 0 * lat}, {}}}};

const cm::Route kOrderRoute{kPoints[3][0], kPoints[3][1]};

const cm::Route kContractorRoute{kPoints[0][0], kPoints[0][1], kPoints[1][0],
                                 kPoints[2][0], kPoints[2][1], kPoints[1][1]};

auto MakeOrder(const std::string& id,
               const std::chrono::system_clock::time_point& date_drive,
               std::chrono::seconds plan_transporting_time,
               const cm::RoutePoint& source = {},
               const cm::RoutePoint& destination = {}) {
  cm::Order order;
  order.order_id = id;
  order.taxi_status = ::order_access::models::TaxiStatus::Transporting;
  order.ready_status = cm::OrderReadyStatus::kPending;
  order.driving_started_at = date_drive;
  order.plan_transporting_time = plan_transporting_time;
  if (source.position) {
    order.source = *source.position;
  }
  if (destination.position) {
    order.destination = *destination.position;
  }
  return order;
}

const cm::ContractorOrders& kContractorOrders{
    {MakeOrder("order_id1", TimePoint{0s}, 6s, kPoints[1][0], kPoints[1][1]),
     MakeOrder("order_id2", TimePoint{1s}, 4s, kPoints[2][0], kPoints[2][1])}};

const std::vector<cm::RouteVariant> kVariants{
    {{kPoints[1][0], kPoints[2][0], kContractorPoint, kPoints[3][0],
      kPoints[2][1], kPoints[3][1], kPoints[1][1]},
     true,
     false,
     0.6666666666666667,
     {{"in_driving_0", 0},
      {"in_driving_1", 0},
      {"in_transporting_1", 1},
      {"in_driving_2", 0},
      {"azimuth_cb_0", 90},
      {"in_waiting_2", 0},
      {"in_waiting_0", 0},
      {"azimuth_cb_1", 90},
      {"azimuth_ca_0", 270},
      {"azimuth_cb_2", 90},
      {"base_transporting_time_0", 6},
      {"base_past_time_1", 1},
      {"base_left_time_2", 2},
      {"base_past_time_0", 2},
      {"base_transporting_dist_2", 0},
      {"base_transporting_dist_0", 0},
      {"azimuth_ca_1", 270},
      {"base_driving_time_2", 1},
      {"base_left_dist_0", 0},
      {"base_left_dist_1", 0},
      {"base_driving_time_1", 0},
      {"base_driving_dist_1", 0},
      {"base_transporting_dist_1", 0},
      {"base_transporting_time_1", 4},
      {"base_left_dist_2", 0},
      {"in_transporting_0", 1},
      {"base_driving_dist_2", 0},
      {"base_transporting_time_2", 1},
      {"base_driving_time_0", 0},
      {"driving_time_0", 0},
      {"transporting_time_0", 8},
      {"azimuth_ca_2", 90},
      {"base_driving_dist_0", 0},
      {"left_dist_0", 0},
      {"base_left_time_0", 4},
      {"left_time_0", 6},
      {"driving_dist_0", 0},
      {"transporting_time_1", 4},
      {"driving_time_1", 0},
      {"in_waiting_1", 0},
      {"transporting_time_2", 3},
      {"base_left_time_1", 3},
      {"past_time_2", 0},
      {"in_transporting_2", 0},
      {"left_dist_1", 0},
      {"base_past_time_2", 0},
      {"driving_dist_1", 0},
      {"past_time_1", 1},
      {"past_time_0", 2},
      {"transporting_dist_1", 0},
      {"left_time_1", 3},
      {"transporting_dist_0", 0},
      {"transporting_dist_2", 0},
      {"driving_dist_2", 0},
      {"left_dist_2", 0},
      {"left_time_2", 4},
      {"driving_time_2", 1}},
     {},
     {}},
    {{kPoints[1][0], kPoints[2][0], kContractorPoint, kPoints[3][0],
      kPoints[2][1], kPoints[1][1], kPoints[3][1]},
     true,
     false,
     0.8,
     {{"in_driving_0", 0},
      {"in_driving_1", 0},
      {"in_transporting_1", 1},
      {"in_driving_2", 0},
      {"azimuth_cb_0", 90},
      {"in_waiting_2", 0},
      {"in_waiting_0", 0},
      {"azimuth_cb_1", 90},
      {"azimuth_ca_0", 270},
      {"azimuth_cb_2", 90},
      {"base_transporting_time_0", 6},
      {"base_past_time_1", 1},
      {"base_left_time_2", 2},
      {"base_past_time_0", 2},
      {"base_transporting_dist_2", 0},
      {"base_transporting_dist_0", 0},
      {"azimuth_ca_1", 270},
      {"base_driving_time_2", 1},
      {"base_left_dist_0", 0},
      {"base_left_dist_1", 0},
      {"base_driving_time_1", 0},
      {"base_driving_dist_1", 0},
      {"base_transporting_dist_1", 0},
      {"base_transporting_time_1", 4},
      {"base_left_dist_2", 0},
      {"in_transporting_0", 1},
      {"base_driving_dist_2", 0},
      {"base_transporting_time_2", 1},
      {"base_driving_time_0", 0},
      {"driving_time_0", 0},
      {"transporting_time_0", 6},
      {"azimuth_ca_2", 90},
      {"base_driving_dist_0", 0},
      {"left_dist_0", 0},
      {"base_left_time_0", 4},
      {"left_time_0", 4},
      {"driving_dist_0", 0},
      {"transporting_time_1", 4},
      {"driving_time_1", 0},
      {"in_waiting_1", 0},
      {"transporting_time_2", 5},
      {"base_left_time_1", 3},
      {"past_time_2", 0},
      {"in_transporting_2", 0},
      {"left_dist_1", 0},
      {"base_past_time_2", 0},
      {"driving_dist_1", 0},
      {"past_time_1", 1},
      {"past_time_0", 2},
      {"transporting_dist_1", 0},
      {"left_time_1", 3},
      {"transporting_dist_0", 0},
      {"transporting_dist_2", 0},
      {"driving_dist_2", 0},
      {"left_dist_2", 0},
      {"left_time_2", 6},
      {"driving_time_2", 1}},
     {},
     {}},
    {{kPoints[1][0], kPoints[2][0], kContractorPoint, kPoints[3][0],
      kPoints[3][1], kPoints[2][1], kPoints[1][1]},
     false,
     true,
     0.,
     {{"in_driving_0", 0},
      {"in_driving_1", 0},
      {"in_transporting_1", 1},
      {"in_driving_2", 0},
      {"azimuth_cb_0", 90},
      {"in_waiting_2", 0},
      {"in_waiting_0", 0},
      {"azimuth_cb_1", 90},
      {"azimuth_ca_0", 270},
      {"azimuth_cb_2", 90},
      {"base_transporting_time_0", 6},
      {"base_past_time_1", 1},
      {"base_left_time_2", 2},
      {"base_past_time_0", 2},
      {"base_transporting_dist_2", 0},
      {"base_transporting_dist_0", 0},
      {"azimuth_ca_1", 270},
      {"base_driving_time_2", 1},
      {"base_left_dist_0", 0},
      {"base_left_dist_1", 0},
      {"base_driving_time_1", 0},
      {"base_driving_dist_1", 0},
      {"base_transporting_dist_1", 0},
      {"base_transporting_time_1", 4},
      {"base_left_dist_2", 0},
      {"in_transporting_0", 1},
      {"base_driving_dist_2", 0},
      {"base_transporting_time_2", 1},
      {"base_driving_time_0", 0},
      {"driving_time_0", 0},
      {"transporting_time_0", 6},
      {"azimuth_ca_2", 90},
      {"base_driving_dist_0", 0},
      {"left_dist_0", 0},
      {"base_left_time_0", 4},
      {"left_time_0", 4},
      {"driving_dist_0", 0},
      {"transporting_time_1", 4},
      {"driving_time_1", 0},
      {"in_waiting_1", 0},
      {"transporting_time_2", 1},
      {"base_left_time_1", 3},
      {"past_time_2", 0},
      {"in_transporting_2", 0},
      {"left_dist_1", 0},
      {"base_past_time_2", 0},
      {"driving_dist_1", 0},
      {"past_time_1", 1},
      {"past_time_0", 2},
      {"transporting_dist_1", 0},
      {"left_time_1", 3},
      {"transporting_dist_0", 0},
      {"transporting_dist_2", 0},
      {"driving_dist_2", 0},
      {"left_dist_2", 0},
      {"left_time_2", 2},
      {"driving_time_2", 1}

     },
     {},
     {}}};

const auto kFilterExpr = math_expr::Parse(R"(
    transporting_time_0 - base_transporting_time_0 > delta
  || transporting_time_1 - base_transporting_time_1 > delta
  || transporting_time_2 - base_transporting_time_2 > delta)");

const auto kScoreExpr = math_expr::Parse("1 - 1 / transporting_time_2");

const cm::RouteParameters kConfigParameters{{"delta", 1}};

const cc::TestRouting kRouting;

}  // namespace

namespace combo_contractors::models {

// Pretty printers

inline void PrintTo(const RouteVariant& variant, std::ostream* os) {
  formats::json::ValueBuilder builder;
  builder = variant;
  *os << ToString(builder.ExtractValue());
}

inline void PrintTo(const RoutePoint& point, std::ostream* os) {
  formats::json::ValueBuilder builder;
  builder = point;
  *os << ToString(builder.ExtractValue());
}

}  // namespace combo_contractors::models

TEST(MatchHelper, GetResults) {
  cm::MatchHelper helper{kContractorRoute,
                         kOrderRoute,
                         kFilterExpr,
                         kScoreExpr,
                         kContractorPosition,
                         geometry::Azimuth{5 * geometry::degree},
                         {},
                         kConfigParameters,
                         kRouting,
                         {},
                         kContractorOrders,
                         false,
                         {},
                         {},
                         {}};
  RunInCoro([&helper] {
    const auto now = TimePoint{4s};
    helper.StartMatching();
    helper.GetResults(now);
  });
  ASSERT_EQ(helper.variants.size(), kVariants.size());

  std::vector<testing::Matcher<cm::RouteVariant>> matchers;
  for (const auto& variant : kVariants) {
    std::vector<testing::Matcher<std::pair<std::string, double>>>
        param_matchers;

    for (const auto& [key, value] : variant.parameters) {
      param_matchers.push_back(testing::AllOf(
          testing::Field("first", &std::pair<std::string, double>::first, key),
          testing::Field("second", &std::pair<std::string, double>::second,
                         testing::DoubleEq(value))));
    }

    matchers.push_back(testing::AllOf(
        testing::Field("route", &cm::RouteVariant::route,
                       testing::ElementsAreArray(variant.route)),
        testing::Field("score", &cm::RouteVariant::score,
                       testing::DoubleEq(variant.score)),
        testing::Field("is_filtered", &cm::RouteVariant::is_filtered,
                       variant.is_filtered),
        testing::Field("parameters", &cm::RouteVariant::parameters,
                       testing::UnorderedElementsAreArray(param_matchers))));
  }

  ASSERT_THAT(helper.variants, testing::ElementsAreArray(matchers));
}

TEST(MatchHelper, StartMatching) {
  cm::MatchHelper helper{kContractorRoute,
                         kOrderRoute,
                         kFilterExpr,
                         kScoreExpr,
                         kContractorPosition,
                         {},
                         {},
                         kConfigParameters,
                         kRouting,
                         {},
                         kContractorOrders,
                         true,
                         {},
                         {},
                         {}};
  RunInCoro([&helper] { helper.StartMatching(); });
  ASSERT_EQ(helper.variants.size(), 1);
  ASSERT_THAT(helper.variants[0],
              testing::Field("route", &cm::RouteVariant::route,
                             testing::ElementsAreArray(kVariants[2].route)));
}
