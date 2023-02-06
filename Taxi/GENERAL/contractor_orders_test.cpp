#include <gmock/gmock-matchers.h>
#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <models/contractor_orders.hpp>

namespace cm = combo_contractors::models;

using namespace std::chrono_literals;
using geometry::lat;
using geometry::lon;
using Type = cm::RoutePointType;
using Position = geometry::Position;

TEST(ContractorOrders, GetComboInfoOuterCancelledInDriving) {
  std::vector<cm::RoutePoint> route{
      {"oid0", Type::kStart, Position{0 * lat, 0 * lon}, {}},
      {"oid1", Type::kStart, Position{0 * lat, 0 * lon}, {}},
      {"oid1", Type::kFinish, Position{0 * lat, 0 * lon}, {}},
      {"oid0", Type::kFinish, Position{0 * lat, 0 * lon}, {}}};

  std::vector<cm::Order> orders;

  cm::Order order;
  order.order_id = "oid0";
  order.source = *route[0].position;
  order.destination = *route[3].position;
  order.taxi_status = order_access::models::TaxiStatus::Cancelled;
  order.ready_status = cm::OrderReadyStatus::kFinished;
  order.driving_started_at = std::chrono::system_clock::time_point{0s};

  orders.push_back(order);

  order.order_id = "oid1";
  order.source = *route[1].position;
  order.destination = *route[2].position;
  order.taxi_status = order_access::models::TaxiStatus::Driving;
  order.ready_status = cm::OrderReadyStatus::kPending;
  order.combo_info = {true, route, {}, {}, {}, {}, {}, {}};
  order.driving_started_at = std::chrono::system_clock::time_point{1s};

  orders.push_back(order);

  cm::ContractorOrders contractor_orders{orders};
  const auto combo_info = contractor_orders.GetComboInfo();

  std::vector<cm::RoutePoint> expected_route{
      {"oid1", Type::kStart, Position{0 * lat, 0 * lon}, {}},
      {"oid1", Type::kFinish, Position{0 * lat, 0 * lon}, {}},
  };

  std::vector<testing::Matcher<cm::RoutePoint>> matchers;

  for (const auto& point : expected_route) {
    matchers.push_back(testing::AllOf(
        testing::Field("order_id", &cm::RoutePoint::order_id, point.order_id),
        testing::Field("type", &cm::RoutePoint::type, point.type)));
  }

  ASSERT_EQ(combo_info.route.size(), expected_route.size());
  ASSERT_THAT(combo_info.route, testing::ElementsAreArray(matchers));
}
