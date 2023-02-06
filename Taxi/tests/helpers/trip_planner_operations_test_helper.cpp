#include "trip_planner_operations_test_helper.hpp"

#include <utils/algo.hpp>

#include <tests/helpers/interlayers/route_info.hpp>
#include <tests/helpers/interlayers/search_result_info.hpp>
#include <tests/helpers/interlayers/shuttle_info.hpp>
#include <tests/helpers/route_cache_test_helper.hpp>
#include <tests/parsers/common.hpp>
#include <tests/parsers/trip_planner_operations.hpp>

namespace {

namespace op = shuttle_control::trip_planner::operations;
namespace mdl = shuttle_control::models;
namespace prs = shuttle_control::tests::parsers;
namespace hlp = shuttle_control::tests::helpers;

struct Definitions {
  std::unordered_map<mdl::RouteIdT, hlp::interlayers::RouteInfo> routes_info;
  std::unordered_map<mdl::ShuttleIdT, hlp::interlayers::ShuttleInfo>
      shuttles_info;

  const mdl::Route& GetRoute(const mdl::RouteIdT& route_id) const {
    const auto& route_it = routes_info.find(route_id);
    UINVARIANT(route_it != routes_info.end(),
               "Cannot find route with id: " +
                   std::to_string(route_id.GetUnderlying()));
    return route_it->second.route;
  }

  const hlp::interlayers::ShuttleInfo& GetShuttle(
      const mdl::ShuttleIdT& shuttle_id) const {
    const auto& shuttle_it = shuttles_info.find(shuttle_id);
    UINVARIANT(shuttle_it != shuttles_info.end(),
               "Cannot find shuttle with id: " +
                   std::to_string(shuttle_id.GetUnderlying()));
    return shuttle_it->second;
  }
};

Definitions Parse(const ::formats::json::Value& value,
                  ::formats::parse::To<Definitions>) {
  return Definitions{
      prs::ParseToMap<
          std::unordered_map<mdl::RouteIdT, hlp::interlayers::RouteInfo>>(
          value["routes"],
          [](const hlp::interlayers::RouteInfo& it) {
            return it.route.GetMeta().id;
          }),
      prs::ParseToMap<
          std::unordered_map<mdl::ShuttleIdT, hlp::interlayers::ShuttleInfo>>(
          value["shuttles"],
          [](const hlp::interlayers::ShuttleInfo& it) {
            return it.shuttle_desc.shuttle_id;
          }),
  };
}

struct TestHelperInfo {
  op::SearchQuery query;
  hlp::interlayers::SearchResultInfo search_result_scope;

  Definitions definitions_scope;
};

TestHelperInfo Parse(const ::formats::json::Value& value,
                     ::formats::parse::To<TestHelperInfo>) {
  return TestHelperInfo{
      value["query"].As<op::SearchQuery>(),
      value["result"].As<hlp::interlayers::SearchResultInfo>(),
      value["definitions"].As<Definitions>(),
  };
}

}  // namespace

namespace shuttle_control::tests::helpers {

TripPlannerOpearationTestHelper TripPlannerOpearationTestHelper::Build(
    const ::formats::json::Value& value) {
  namespace op = trip_planner::operations;

  auto&& [query, result_info, definitions] = value.As<TestHelperInfo>();

  TripPlannerOpearationTestHelper test_helper{};

  test_helper.query = std::move(query);

  test_helper.route_cache =
      RouteCacheTestHelper::Build(definitions.routes_info).routes_cache;

  test_helper.result.car_ab_info = std::move(result_info.car_ab_info);
  test_helper.result.walk_ab_info = std::move(result_info.walk_ab_info);
  test_helper.result.pdp_prepare_response =
      std::move(result_info.pdp_prepare_response);
  for (auto& [route_id, route_info] : result_info.routes_info) {
    op::RouteLevelResult route_level_result{route_id, {}};

    for (auto& [segment_id, segment_info] : route_info.segments_info) {
      op::SegmentLevelResult segment_level_result{
          segment_id,
          std::move(segment_info.to_pickup),
          std::move(segment_info.from_dropoff),
          {},
      };

      for (auto& [shuttle_id, shuttle_info] : segment_info.shuttles_info) {
        const auto& shuttle = definitions.GetShuttle(shuttle_id);
        const auto& route = definitions.GetRoute(shuttle.shuttle_desc.route_id);

        models::Route shifted_route{route};
        if (shuttle.shift_route_to) {
          shifted_route.ShiftToStop(shuttle.shift_route_to.value());
        }

        op::ShuttleLevelResult shuttle_level_result{
            shuttle_id,
            shuttle.shuttle_desc,
            std::move(shifted_route),
            shuttle.stateful_position,
            shuttle.direction,
            shuttle.next_stop_info,
            shuttle.bookings,
            {},
        };

        for (auto& [trip_id, trip_info] : shuttle_info.trips) {
          if (trip_info.trip_route_id) {
            UINVARIANT(!trip_info.trip_level_result.trip_route,
                       "Both trip_route and trip_route_id present for trip " +
                           boost::uuids::to_string(trip_id));
            auto trip_route = definitions.GetRoute(*trip_info.trip_route_id);
            if (shuttle.shift_route_to) {
              trip_route.ShiftToStop(*shuttle.shift_route_to);
            }
            trip_info.trip_level_result.trip_route = std::move(trip_route);
          }
          shuttle_level_result.trips.emplace(trip_id,
                                             trip_info.trip_level_result);
        }

        segment_level_result.shuttles.emplace(shuttle_id,
                                              std::move(shuttle_level_result));
      }

      route_level_result.segments.emplace(segment_id,
                                          std::move(segment_level_result));
    }

    test_helper.result.routes.emplace(route_id, std::move(route_level_result));
  }

  return test_helper;
}

bool TripPlannerOpearationTestHelper::operator==(
    const TripPlannerOpearationTestHelper& other) const {
  return query == other.query && result == other.result &&
         route_cache == other.route_cache;
}

}  // namespace shuttle_control::tests::helpers
