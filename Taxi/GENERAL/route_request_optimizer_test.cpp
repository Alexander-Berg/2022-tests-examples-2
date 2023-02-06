#include "route_request_optimizer.hpp"

#include <userver/utest/utest.hpp>

using namespace driver_route_watcher::models;
using namespace driver_route_watcher::internal;
using namespace ::geometry::literals;

namespace {
const ::geometry::Position kX = {37.0_lon, 53.5_lat};
const ::geometry::Position kY = {37.5_lon, 53.0_lat};

const ::geometry::Position kA = {37.5_lon, 53.5_lat};
const ::geometry::Position kB = {38.0_lon, 54.0_lat};
const ::geometry::Position kC = {38.5_lon, 54.5_lat};
const ::geometry::Position kD = {39.0_lon, 55.0_lat};
const ::geometry::Position kE = {39.5_lon, 55.5_lat};

const ::geometry::Azimuth kSourceDirection = ::geometry::Azimuth::from_value(5);

struct TestData {
  SourcePosition source;
  std::vector<TrackedDestinationPoint> actual_tracked_points;
  std::vector<TrackedDestinationPoint> previous_tracked_points;
  Route previous_route;
  std::vector<RouteRequestInfo> reference_result;
  ::geometry::Distance acceptable_delta;
};

void PrintTo(const TestData& data, std::ostream* os) {
  if (!os) {
    return;
  }

  *os << "{"
      << "source: " << data.source << "; "
      << "actual_tracked_points {}" << data.actual_tracked_points.size() << "}";
}

struct ConnectedPoint {
  ::geometry::Position position;
  bool is_connected;
};

TrackedDestinationPoint MakeTestTrackedDestinationPoint(
    const ::geometry::Position& destination, bool is_connected) {
  return TrackedDestinationPoint{DestinationPoint{destination},
                                 ServiceId("some_service_id"),
                                 is_connected,
                                 std::nullopt,
                                 1.0,
                                 false,
                                 std::nullopt,
                                 std::nullopt,
                                 "some_meta_info"};
}

std::vector<::routing_base::Leg> MakeLegs(
    const std::vector<::geometry::Position>& path) {
  UINVARIANT(path.size() > 1, "Invalid path");

  std::vector<::routing_base::Leg> result;

  result.reserve(path.size() - 1);
  for (size_t i = 0; i + 1 < path.size(); ++i) {
    result.push_back({i});
  }

  return result;
}

Route MakeTestRoute(const std::vector<::geometry::Position>& path,
                    const std::vector<::routing_base::Leg>& legs) {
  Route result;

  for (size_t i = 0; i < path.size(); ++i) {
    result.path.push_back(clients::routing::RoutePoint{path[i]});
  }
  result.legs = legs;

  return result;
}

TestData MakeTestData(const SourcePosition& source,
                      const std::vector<ConnectedPoint>& actual_path,
                      const ::geometry::Position& previous_source,
                      const std::vector<ConnectedPoint>& previous_path,
                      const std::vector<RouteRequestInfo>& reference,
                      const ::geometry::Distance& acceptable_delta) {
  TestData result;

  std::vector<TrackedDestinationPoint> actual;
  for (const auto& point : actual_path) {
    actual.push_back(
        MakeTestTrackedDestinationPoint(point.position, point.is_connected));
  }

  std::vector<TrackedDestinationPoint> previous;
  std::vector<::geometry::Position> previous_route_path = {previous_source};
  for (const auto& point : previous_path) {
    previous.push_back(
        MakeTestTrackedDestinationPoint(point.position, point.is_connected));
    previous_route_path.push_back(point.position);
  }

  result.source = source;
  result.actual_tracked_points = std::move(actual);
  result.previous_tracked_points = std::move(previous);
  result.previous_route =
      MakeTestRoute(previous_route_path, MakeLegs(previous_route_path));
  result.reference_result = reference;
  result.acceptable_delta = acceptable_delta;

  return result;
}

[[maybe_unused]] void PrintPathTo(const std::optional<Route>& route,
                                  std::ostream& out = std::cerr) {
  out << "[ ";
  if (route) {
    for (const auto& point : route->path) {
      out << point << "";
    }
  }
  out << " ]" << std::endl;
}

}  // namespace

struct RequestOptimizerTestFixture : public testing::TestWithParam<TestData> {
  static inline const ::geometry::Distance kAcceptAllDelta =
      ::geometry::Distance::from_value(1000000);
  static inline const ::geometry::Distance kLimitedDelta =
      ::geometry::Distance::from_value(100);

  // X - actual driver position (source)
  // Y - previous (unknown) route source
  //
  //    actual itinerary   |  previous itinerary |        answer
  // 1. [B]                | [A, B]              | (Y->A->B) -> (Y->B)
  // 2. [A, B]             | [A, B, C]           | (Y->A->B->C) -> ()
  // 3. [A], [A, B],       | [A], [A, D], [D, E] | (Y->A)(A->D)(D->E) ->
  //    [B, C, D], [D, E]  |                     | (Y->A)()()(D->E)
  // 4. [C], [C, D]        | [A], [A, B], [B, C] | (Y->A)(A->B)(B->C)(C->D)
  //                       | [C, D]              | -> (Y->C)(C->D)
  // 5. [C], [C, D]        | [A, B, C], [C, D]   | (Y->A->B->C)(C->D) ->
  //                       |                     | (Y->C)(C->D)
  // 6. [C, D], [D, E]     | [A, B, C, D]        | (Y->A->B->C->D) ->
  //                       |                     | (Y->A->B->C->D)()
  // 7. [A, B]             | []                  | () -> ()
  // 8. [A], [A, B]        | []                  | () -> ()
  static inline std::vector<TestData> base_cases = {
      // 1. [B]                | [A, B]              | (Y->A->B) -> (Y->B)
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kB, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, true}},
          // Reference route request infos
          {{{{kX, kB}, kSourceDirection}, MakeTestRoute({kY, kA, kB}, {{0}})}},
          // Acceptable delta
          kAcceptAllDelta),
      // 2. [A, B]             | [A, B, C]           | (Y->A->B->C) -> ()
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kA, false}, {kB, true}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, true}, {kC, true}},
          // Reference route request infos
          {{{{kX, kA, kB}, kSourceDirection}, std::nullopt}},
          // Acceptable delta
          kAcceptAllDelta),
      // 3. [A], [A, B],       | [A], [A, D], [D, E] | (Y->A)(A->D)(D->E) ->
      //    [B, C, D], [D, E]  |                     | (Y->A)()()(D->E)
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kA, false}, {kB, false}, {kC, false}, {kD, true}, {kE, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kD, false}, {kE, false}},
          // Reference route request infos
          {{{{kX, kA}, kSourceDirection}, MakeTestRoute({kY, kA}, {{0}})},
           {{{kA, kB}, std::nullopt}, std::nullopt},
           {{{kB, kC, kD}, std::nullopt}, std::nullopt},
           {{{kD, kE}, std::nullopt}, MakeTestRoute({kD, kE}, {{0}})}},
          // Acceptable delta
          kAcceptAllDelta),
      // 4. [C], [C, D]        | [A], [A, B], [B, C] | (Y->A)(A->B)(B->C)(C->D)
      //                       | [C, D]              | -> (B->C)(C->D)
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kC, false}, {kD, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, false}, {kC, false}, {kD, false}},
          // Reference route request infos
          {{{{kX, kC}, kSourceDirection}, MakeTestRoute({kB, kC}, {{0}})},
           {{{kC, kD}, std::nullopt}, MakeTestRoute({kC, kD}, {{0}})}},
          // Acceptable delta
          kAcceptAllDelta),
      // 5. [C], [C, D]        | [A, B, C], [C, D]   | (Y->A->B->C)(C->D) ->
      //                       |                     | (Y->C)(C->D)
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kC, false}, {kD, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, true}, {kC, true}, {kD, false}},
          // Reference route request infos
          {{{{kX, kC}, kSourceDirection},
            MakeTestRoute({kY, kA, kB, kC}, {{0}})},
           {{{kC, kD}, std::nullopt}, MakeTestRoute({kC, kD}, {{0}})}},
          // Acceptable delta
          kAcceptAllDelta),
      // 6. [C, D], [D, E]     | [A, B, C, D]        | (Y->A->B->C->D) ->
      //                       |                     | (Y->A->B->C->D)()
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kC, true}, {kD, true}, {kE, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, true}, {kC, true}, {kD, true}},
          // Reference route request infos
          {{{{kX, kC, kD}, kSourceDirection},
            MakeTestRoute({kY, kA, kB, kC, kD}, {{0}, {3}})},
           {{{kD, kE}, std::nullopt}, std::nullopt}},
          // Acceptable delta
          kAcceptAllDelta),
      // 7. [A, B]             | []                  | () -> ()
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kA, false}, {kB, true}},
          // Previous source position
          kY,
          // Previous itinerary
          {{}},
          // Reference route request infos
          {{{{kX, kA, kB}, kSourceDirection}, std::nullopt}},
          // Acceptable delta
          kAcceptAllDelta),
      // 8. [A], [A, B]        | []                  | () -> ()
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kA, true}, {kB, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{}},
          // Reference route request infos
          {{{{kX, kA}, kSourceDirection}, std::nullopt},
           {{{kA, kB}, std::nullopt}, std::nullopt}},
          // Acceptable delta
          kAcceptAllDelta)};

  // X - actual driver position (source)
  // Y - previous (unknown) route source
  //
  //    actual itinerary   |  previous itinerary |        answer
  // 1. [B]                | [A, B]              | (Y->A->B) -> ()
  // 2. [A], [A, B],       | [A], [A, D], [D, E] | (Y->A)(A->D)(D->E) ->
  //    [B, C, D], [D, E]  |                     | ()()()(D->E)
  // 3. [C], [C, D]        | [A], [A, B], [B, C] | (Y->A)(A->B)(B->C)(C->D)
  //                       | [C, D]              | -> ()(C->D)
  // 4. [C], [C, D]        | [A, B, C], [C, D]   | (Y->A->B->C)(C->D) ->
  //                       |                     | ()(C->D)
  // 5. [C, D], [D, E]     | [A, B, C, D]        | (Y->A->B->C->D) -> ()()
  //
  // We can't reuse first segment of route because the acceptable delta so
  // small, and it is necessary to rebuild this segment
  static inline std::vector<TestData> prefix_cases = {
      // 1. [B]                | [A, B]              | (Y->A->B) -> ()
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kB, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, true}},
          // Reference route request infos
          {{{{kX, kB}, kSourceDirection}, std::nullopt}},
          // Acceptable delta
          kLimitedDelta),
      // 2. [A], [A, B],       | [A], [A, D], [D, E] | (Y->A)(A->D)(D->E) ->
      //    [B, C, D], [D, E]  |                     | ()()()(D->E)
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kA, false}, {kB, false}, {kC, false}, {kD, true}, {kE, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kD, false}, {kE, false}},
          // Reference route request infos
          {{{{kX, kA}, kSourceDirection}, MakeTestRoute({kY, kA}, {{0}})},
           {{{kA, kB}, std::nullopt}, std::nullopt},
           {{{kB, kC, kD}, std::nullopt}, std::nullopt},
           {{{kD, kE}, std::nullopt}, MakeTestRoute({kD, kE}, {{0}})}},
          // Acceptable delta
          kLimitedDelta),
      // 3. [C], [C, D]        | [A], [A, B], [B, C] | (Y->A)(A->B)(B->C)(C->D)
      //                       | [C, D]              | -> ()(C->D)
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kC, false}, {kD, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, false}, {kC, false}, {kD, false}},
          // Reference route request infos
          {{{{kX, kC}, kSourceDirection}, std::nullopt},
           {{{kC, kD}, std::nullopt}, MakeTestRoute({kC, kD}, {{0}})}},
          // Acceptable delta
          kLimitedDelta),
      // 4. [C], [C, D]        | [A, B, C], [C, D]   | (Y->A->B->C)(C->D) ->
      //                       |                     | ()(C->D)
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kC, false}, {kD, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, true}, {kC, true}, {kD, false}},
          // Reference route request infos
          {{{{kX, kC}, kSourceDirection}, std::nullopt},
           {{{kC, kD}, std::nullopt}, MakeTestRoute({kC, kD}, {{0}})}},
          // Acceptable delta
          kLimitedDelta),
      // 5. [C, D], [D, E]     | [A, B, C, D]        | (Y->A->B->C->D) ->
      //                       |                     | ()()
      MakeTestData(
          // Source position with direction
          {kX, kSourceDirection},
          // Actual itinerary
          {{kC, true}, {kD, true}, {kE, false}},
          // Previous source position
          kY,
          // Previous itinerary
          {{kA, false}, {kB, true}, {kC, true}, {kD, true}},
          // Reference route request infos
          {{{{kX, kC, kD}, kSourceDirection}, std::nullopt},
           {{{kD, kE}, std::nullopt}, std::nullopt}},
          // Acceptable delta
          kLimitedDelta)};
};

TEST_P(RequestOptimizerTestFixture, TestCorrectness) {
  const auto& test_data = GetParam();
  Itinerary actual{test_data.actual_tracked_points};
  ItineraryWithRoute previous{test_data.previous_tracked_points,
                              test_data.previous_route};
  EXPECT_EQ(actual.ConnectedSegmentsCount(), test_data.reference_result.size());

  auto route_request_infos = RouteRequestOptimizer::GetRouteRequestInfos(
      test_data.source, actual, previous, test_data.acceptable_delta);

  EXPECT_EQ(route_request_infos.size(), test_data.reference_result.size());
  for (size_t i = 0; i < std::min(route_request_infos.size(),
                                  test_data.reference_result.size());
       ++i) {
    // std::cerr << "Infos number: " << i << std::endl;
    const auto& first = route_request_infos[i];
    const auto& second = test_data.reference_result[i];

    // Check request data
    EXPECT_EQ(first.request_data.path, second.request_data.path);
    EXPECT_TRUE(first.request_data.direction == second.request_data.direction);

    // Check route
    EXPECT_TRUE(first.route.has_value() == second.route.has_value());
    //    std::cerr << "First route: ";
    //    PrintPathTo(first.route);
    //    std::cerr << "Second route: ";
    //    PrintPathTo(second.route);
    if (first.route && second.route) {
      EXPECT_EQ(first.route->path, second.route->path);
      EXPECT_EQ(first.route->legs.size(), second.route->legs.size());

      //      std::cerr << "First legs: ";
      //      for (const auto& leg : first.route->legs) {
      //        std::cerr << leg.point_index << " ";
      //      }
      //      std::cerr << std::endl;
      //      std::cerr << "Second legs: ";
      //      for (const auto& leg : second.route->legs) {
      //        std::cerr << leg.point_index << " ";
      //      }
      //      std::cerr << std::endl;

      for (size_t j = 0;
           j < std::min(first.route->legs.size(), second.route->legs.size());
           ++j) {
        EXPECT_EQ(first.route->legs[j].point_index,
                  second.route->legs[j].point_index);
      }
    }
  }
}

INSTANTIATE_TEST_SUITE_P(
    BaseTestCases, RequestOptimizerTestFixture,
    testing::ValuesIn(RequestOptimizerTestFixture::base_cases));

INSTANTIATE_TEST_SUITE_P(
    PrefixTestCases, RequestOptimizerTestFixture,
    testing::ValuesIn(RequestOptimizerTestFixture::prefix_cases));
