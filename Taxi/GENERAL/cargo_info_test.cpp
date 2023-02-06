#include "cargo_info.hpp"

#include <userver/utils/datetime.hpp>

#include <gtest/gtest.h>

TEST(GetRoutePoints, NoPointsForOrder) {
  clients::b2b_taxi::SearchedClaimMP claim;
  claim.route_points.resize(2);
  claim.route_points[0].id = 0;
  claim.route_points[0].external_order_id = "0";
  claim.route_points[0].type = clients::b2b_taxi::PointType::kDestination;
  claim.route_points[0].visit_order = 0;

  claim.route_points[1].id = 1;
  claim.route_points[1].external_order_id = "1";
  claim.route_points[1].type = clients::b2b_taxi::PointType::kDestination;
  claim.route_points[1].visit_order = 1;

  const auto route_points = eats_eta::utils::GetRoutePoints(claim, "2");
  ASSERT_EQ(route_points.first.has_value(), false);
  ASSERT_EQ(route_points.second.has_value(), false);
}

TEST(GetRoutePoints, EmptySourcePoints) {
  clients::b2b_taxi::SearchedClaimMP claim;
  claim.route_points.resize(2);
  claim.route_points[0].id = 0;
  claim.route_points[0].external_order_id = "nr";
  claim.route_points[0].type = clients::b2b_taxi::PointType::kDestination;
  claim.route_points[0].visit_order = 0;

  claim.route_points[1].id = 1;
  claim.route_points[1].external_order_id = "nr";
  claim.route_points[1].type = clients::b2b_taxi::PointType::kReturn;
  claim.route_points[1].visit_order = 1;

  const auto route_points = eats_eta::utils::GetRoutePoints(claim, "nr");
  ASSERT_EQ(route_points.first.has_value(), false);
  ASSERT_EQ(route_points.second->id, 0);
}

TEST(GetRoutePoints, EmptyDestinationPoints) {
  clients::b2b_taxi::SearchedClaimMP claim;
  claim.route_points.resize(2);
  claim.route_points[0].id = 0;
  claim.route_points[0].external_order_id = "nr";
  claim.route_points[0].type = clients::b2b_taxi::PointType::kSource;
  claim.route_points[0].visit_order = 0;

  claim.route_points[1].id = 1;
  claim.route_points[0].external_order_id = "nr";
  claim.route_points[1].type = clients::b2b_taxi::PointType::kReturn;
  claim.route_points[0].visit_order = 1;

  const auto route_points = eats_eta::utils::GetRoutePoints(claim, "nr");
  ASSERT_EQ(route_points.first->id, 0);
  ASSERT_EQ(route_points.second.has_value(), false);
}

TEST(GetRoutePoints, SelectMinMax) {
  clients::b2b_taxi::SearchedClaimMP claim;
  claim.route_points.resize(4);
  claim.route_points[0].id = 0;
  claim.route_points[0].external_order_id = "nr";
  claim.route_points[0].type = clients::b2b_taxi::PointType::kSource;
  claim.route_points[0].visit_order = 1;

  claim.route_points[1].id = 1;
  claim.route_points[1].external_order_id = "nr";
  claim.route_points[1].type = clients::b2b_taxi::PointType::kSource;
  claim.route_points[1].visit_order = 0;

  claim.route_points[2].id = 2;
  claim.route_points[2].external_order_id = "nr";
  claim.route_points[2].type = clients::b2b_taxi::PointType::kDestination;
  claim.route_points[2].visit_order = 3;

  claim.route_points[3].id = 3;
  claim.route_points[3].external_order_id = "nr";
  claim.route_points[3].type = clients::b2b_taxi::PointType::kDestination;
  claim.route_points[3].visit_order = 2;

  const auto route_points = eats_eta::utils::GetRoutePoints(claim, "nr");
  ASSERT_EQ(route_points.first->id, 1);
  ASSERT_EQ(route_points.second->id, 2);
}

TEST(GetRoutePoints, Ordering) {
  clients::b2b_taxi::SearchedClaimMP claim;
  claim.route_points.resize(4);
  claim.route_points[0].id = 0;
  claim.route_points[0].external_order_id = "nr";
  claim.route_points[0].type = clients::b2b_taxi::PointType::kSource;
  claim.route_points[0].visit_order = 1;

  claim.route_points[1].id = 1;
  claim.route_points[1].external_order_id = "nr";
  claim.route_points[1].type = clients::b2b_taxi::PointType::kSource;
  claim.route_points[1].visit_order = 1;

  claim.route_points[2].id = 2;
  claim.route_points[2].external_order_id = "nr";
  claim.route_points[2].type = clients::b2b_taxi::PointType::kDestination;
  claim.route_points[2].visit_order = 1;

  claim.route_points[3].id = 3;
  claim.route_points[3].external_order_id = "nr";
  claim.route_points[3].type = clients::b2b_taxi::PointType::kDestination;
  claim.route_points[3].visit_order = 1;

  const auto route_points = eats_eta::utils::GetRoutePoints(claim, "nr");
  ASSERT_EQ(route_points.first->id, 0);
  ASSERT_EQ(route_points.second->id, 2);
}
