#include <gtest/gtest.h>

#include <pricing-extended/helpers/route_analyzer.hpp>

namespace {

using Route = helpers::route_analyzer::Route;
using TestCase = std::tuple<Route, bool>;

class RouteChecker : public ::testing::TestWithParam<TestCase> {};

const Route kOkRoute{
    {48.560118, 51.758128, 89943, 5150}, {48.560327, 51.75821, 89960, 5151},
    {48.560532, 51.758293, 89977, 5152}, {48.56074, 51.758375, 89994, 5153},
    {48.560948, 51.758458, 90011, 5154}, {48.561157, 51.75854, 90028, 5155},
    {48.561365, 51.758617, 90044, 5156}, {48.561572, 51.758692, 90061, 5157}};

const Route kMidBrokenRoute{
    {48.564677, 51.756893, 90596, 5351}, {48.564677, 51.756893, 90596, 5351},
    {48.564677, 51.756893, 90596, 5351}, {48.564677, 51.756893, 90596, 5351},
    {48.564677, 51.756893, 90596, 5351}, {47.8014, 52.0008, 149593, 5442},
    {47.8014, 52.0008, 149593, 5447},    {47.8014, 52.0008, 149593, 5457},
    {47.8014, 52.0008, 149593, 5482},    {47.8014, 52.0008, 149593, 5492},
    {48.56466, 51.75691, 208588, 5506},  {48.56466, 51.75691, 208588, 5507},
    {48.56466, 51.75691, 208588, 5508},  {48.56466, 51.75691, 208588, 5509}};

const Route kBeginBrokenRoute{
    {47.8014, 52.0008, 149593, 5442},   {47.8014, 52.0008, 149593, 5447},
    {47.8014, 52.0008, 149593, 5457},   {47.8014, 52.0008, 149593, 5482},
    {47.8014, 52.0008, 149593, 5492},   {48.56466, 51.75691, 208588, 5506},
    {48.56466, 51.75691, 208588, 5507}, {48.56466, 51.75691, 208588, 5508},
    {48.56466, 51.75691, 208588, 5509}};

}  // namespace

TEST_P(RouteChecker, RouteChecker) {
  const auto& [route, result] = GetParam();
  EXPECT_EQ(helpers::route_analyzer::CheckRoute(route), result);
}

INSTANTIATE_TEST_SUITE_P(RouteChecker, RouteChecker,
                         ::testing::Values(  //
                             std::make_tuple(kOkRoute, true),
                             std::make_tuple(kMidBrokenRoute, false),
                             std::make_tuple(kBeginBrokenRoute, false)));
