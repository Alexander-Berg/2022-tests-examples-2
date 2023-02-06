#include <gtest/gtest.h>

#include <clients/routing/router.hpp>
#include <geometry/distance.hpp>
#include <models/geometry/point.hpp>
#include <models/order_meta.hpp>

#include "controllers/neighbours_searcher.hpp"

#include <components/internal/router_request.hpp>
#include <userver/utest/utest.hpp>

namespace combo_matcher {

namespace {

using components::internal::RouterRequest;
using controllers::scoring::PointToPointTimeAndDists;

class TestRouterQuery : public clients::routing::RouterQuery {
 public:
  void AppendRouter(const clients::routing::RouterQuery::RouterPtr& router) {
    clients::routing::RouterQuery::AppendRouter(router);
  }
};

class TestRouter : public clients::routing::Router {
 public:
  TestRouter()
      : clients::routing::Router(
            clients::routing::RouterVehicleType::kVehicleCar, "router") {}

  bool IsEnabled() const override { return true; };

  bool HasFeatures(
      clients::routing::RouterFeaturesType features) const override {
    return clients::routing::RouterFeatures::kRouteInfo & features;
  }

  clients::routing::RouterResponse<clients::routing::RouteInfo> FetchRouteInfo(
      const clients::routing::Path& path, const clients::routing::DirectionOpt&,
      const clients::routing::RouterSettings& = {},
      const clients::routing::QuerySettings& = {}) const override {
    route_call_count_++;
    clients::routing::RouteInfo ret;
    ret.distance = ::geometry::GreatCircleDistance(path.at(0), path.at(1));
    return ret;
  }

  size_t GetRouteCallCount() const { return route_call_count_; }

 private:
  mutable size_t route_call_count_ = 0;
};

std::pair<models::MatchCandidatesIdxs, std::vector<models::OrderMeta>>
GetOrders() {
  std::vector<models::OrderMeta> orders;

  orders.emplace_back();
  orders.back().point = {92.865575, 55.986885};
  orders.back().point_b = {92.865575, 55.986885};

  orders.emplace_back();
  orders.back().point = {30.370960, 60.050888};
  orders.back().point_b = {30.206501, 59.999286};

  return std::make_pair(models::MatchCandidatesIdxs{0, 1}, orders);
}

}  // namespace

UTEST(Test, RouterRequestTest) {
  const auto& router = std::make_shared<TestRouter>();
  TestRouterQuery router_query;
  router_query.AppendRouter(router);

  const auto& fallback_router = std::make_shared<TestRouter>();
  TestRouterQuery fallback_router_query;
  fallback_router_query.AppendRouter(fallback_router);

  auto [match, orders] = GetOrders();
  RouterRequest request(router_query, fallback_router_query, match, orders);
  request.PerformRequest("router_request");
  auto result = request.Get();
  EXPECT_EQ(router->GetRouteCallCount(), 8);
  for (auto route : PointToPointTimeAndDists::kNecessarySubs) {
    EXPECT_EQ(result.Get(route).dist,
              static_cast<int>(::geometry::GreatCircleDistance(
                                   request.GetPoint(route.From()),
                                   request.GetPoint(route.To()))
                                   .value()));
  }
}

UTEST(Test, FirstPointsAreEqualRouterRequestTest) {
  // When orders first points are equal, RouterRequest is expected to make
  // four calls less to router
  const auto& router = std::make_shared<TestRouter>();
  TestRouterQuery router_query;
  router_query.AppendRouter(router);

  const auto& fallback_router = std::make_shared<TestRouter>();
  TestRouterQuery fallback_router_query;
  fallback_router_query.AppendRouter(fallback_router);

  auto [match, orders] = GetOrders();
  orders[1].point = {92.865575, 55.986885};
  RouterRequest request(router_query, fallback_router_query, match, orders);
  request.PerformRequest("router_request");
  auto result = request.Get();
  EXPECT_EQ(router->GetRouteCallCount(), 4);
  for (auto route : PointToPointTimeAndDists::kNecessarySubs) {
    EXPECT_EQ(result.Get(route).dist,
              static_cast<int>(::geometry::GreatCircleDistance(
                                   request.GetPoint(route.From()),
                                   request.GetPoint(route.To()))
                                   .value()));
  }
}

}  // namespace combo_matcher
