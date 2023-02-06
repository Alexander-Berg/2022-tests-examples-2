#include <gtest/gtest.h>

#include <base_calc/base_calc.hpp>
#include <models/serialization/serialize.hpp>

namespace price_calc::base_calc::internal {

RouteParts SplitRouteByGeoareas(const models::Route& route,
                                const Polygons& tariff_geoareas,
                                const models::RidePricesMap& available_rides);

const RouteParts& SplitRouteByGeoareas(
    const models::Route& route, const Polygons& tariff_geoareas,
    const models::RidePricesMap& available_rides,
    const RoutePartsCachingInfo& rpci);

}  // namespace price_calc::base_calc::internal

namespace {

using price_calc::base_calc::Polygons;
using price_calc::models::Point;
using price_calc::models::Polygon;
using price_calc::models::PriceInterval;
using price_calc::models::RidePrices;

static const std::string kGeoareaName1 = "geoarea1";
static const std::string kGeoareaName2 = "geoarea2";
static const std::string kSuburb = "suburb";

static const Polygon kGeoarea1({Point{2, 8}, Point{4, 2}, Point{9, 4},
                                Point{9, 6}},
                               30);
static const Polygon kGeoarea2({Point{7, 5}, Point{10, 9}, Point{13, 2}}, 10);

static const Polygons kPolygons = {{kGeoareaName1, kGeoarea1},
                                   {kGeoareaName2, kGeoarea2}};

static const double kInf = std::numeric_limits<double>::infinity();

static const std::unordered_map<std::string, RidePrices> kRides{
    {kGeoareaName1,
     RidePrices{
         {PriceInterval{60, kInf, 0.25}},  // 0.25 per meter from 60
         {PriceInterval{11, kInf, 0.08}}   // 0.08 per second from 11
     }},
    {kGeoareaName2,
     RidePrices{
         {PriceInterval{0, kInf, 0.7}},  // 0.7 per meter always
         {PriceInterval{20, 60, 0.9},    // 0.9 per second from 20 to 60
          PriceInterval{60, 100, 0.8},   // 0.8 per second from 60 to 100
          PriceInterval{110, 120, 0.6}}  // 0.6 per second from 110 to 120
     }},
    {kSuburb,
     RidePrices{
         {
             PriceInterval{20, 190, 0.3},   // 0.3 per meter from 20 to 190
             PriceInterval{190, kInf, 0.2}  // 0.2 per meter from 190
         },
         {}  // empty time intervals
     }}};

struct GetGeoareaTestData {
  const Point point;
  const std::string geoarea;
};

class GetGeoareaTest : public ::testing::TestWithParam<GetGeoareaTestData> {};

}  // namespace

TEST_P(GetGeoareaTest, GetGeoarea) {
  using price_calc::base_calc::GetGeoarea;

  EXPECT_EQ(GetGeoarea(GetParam().point, kPolygons, kRides),
            GetParam().geoarea);

  // only suburb in available rides => always suburb
  EXPECT_EQ(GetGeoarea(GetParam().point, kPolygons, {{kSuburb, {}}}), kSuburb);
}

INSTANTIATE_TEST_SUITE_P(
    GetGeoareaTest, GetGeoareaTest,
    ::testing::Values(GetGeoareaTestData{Point{4, 4}, kGeoareaName1},
                      GetGeoareaTestData{Point{4, 2}, kGeoareaName1},
                      GetGeoareaTestData{Point{10, 5}, kGeoareaName2},
                      GetGeoareaTestData{Point{8, 5}, kGeoareaName2},
                      GetGeoareaTestData{Point{9, 4.5}, kGeoareaName2},
                      GetGeoareaTestData{Point{10, 7}, kGeoareaName2},
                      GetGeoareaTestData{Point{2, 4}, kSuburb},
                      GetGeoareaTestData{Point{20, 20}, kSuburb},
                      GetGeoareaTestData{Point{9, 3}, kSuburb}));

namespace {

using price_calc::base_calc::PriceAndRouteParts;
using price_calc::base_calc::RoutePart;
using price_calc::base_calc::RouteParts;
using price_calc::base_calc::RoutePartsWithPrices;
using price_calc::base_calc::RoutePartWithPrices;
using price_calc::models::Price;

void ExpectEqual(const Price& actual, const Price& expected) {
  EXPECT_DOUBLE_EQ(actual.boarding, expected.boarding);
  EXPECT_DOUBLE_EQ(actual.distance, expected.distance);
  EXPECT_DOUBLE_EQ(actual.time, expected.time);
  EXPECT_DOUBLE_EQ(actual.waiting, expected.waiting);
  EXPECT_DOUBLE_EQ(actual.requirements, expected.requirements);
  EXPECT_DOUBLE_EQ(actual.transit_waiting, expected.transit_waiting);
  EXPECT_DOUBLE_EQ(actual.destination_waiting, expected.destination_waiting);
}

void ExpectEqual(const RoutePart& actual, const RoutePart& expected) {
  const auto& a = actual;
  const auto& e = expected;
  EXPECT_EQ(a.geoarea, e.geoarea);
  EXPECT_DOUBLE_EQ(a.entrance_distance, e.entrance_distance);
  EXPECT_DOUBLE_EQ(a.entrance_time, e.entrance_time);
  EXPECT_DOUBLE_EQ(a.exit_distance, e.exit_distance);
  EXPECT_DOUBLE_EQ(a.exit_time, e.exit_time);
}

void ExpectEqual(const RouteParts& actual, const RouteParts& expected) {
  // check that expected is valid
  double prev_exit_distance = 0;
  double prev_exit_time = 0;
  for (const auto& route_part : expected) {
    EXPECT_DOUBLE_EQ(route_part.entrance_distance, prev_exit_distance);
    EXPECT_DOUBLE_EQ(route_part.entrance_time, prev_exit_time);
    prev_exit_distance = route_part.exit_distance;
    prev_exit_time = route_part.exit_time;
  }

  // check actual == expected
  EXPECT_EQ(actual.size(), expected.size());
  for (size_t i = 0; i < std::min(actual.size(), expected.size()); ++i) {
    ExpectEqual(actual[i], expected[i]);
  }
}

void ExpectEqual(const RoutePartWithPrices& actual,
                 const RoutePartWithPrices& expected) {
  ExpectEqual(actual.part, expected.part);
  EXPECT_DOUBLE_EQ(actual.price_distance, expected.price_distance);
  EXPECT_DOUBLE_EQ(actual.price_time, expected.price_time);
}

void ExpectEqual(const RoutePartsWithPrices& actual,
                 const RoutePartsWithPrices& expected) {
  EXPECT_EQ(actual.size(), expected.size());

  for (size_t i = 0; i < std::min(actual.size(), expected.size()); ++i) {
    ExpectEqual(actual[i], expected[i]);
  }
}

void ExpectEqual(const PriceAndRouteParts& actual,
                 const PriceAndRouteParts& expected) {
  ExpectEqual(actual.price, expected.price);
  ExpectEqual(actual.route_parts, expected.route_parts);
  EXPECT_EQ(actual.is_transfer, expected.is_transfer);
}

}  // namespace

TEST(BaseCalcInternal, SplitRouteByGeoareas) {
  using price_calc::base_calc::RoutePart;
  using price_calc::base_calc::RoutePartsCache;
  using price_calc::base_calc::RoutePartsCachingInfo;
  using price_calc::base_calc::internal::SplitRouteByGeoareas;
  using price_calc::models::MovementPoint;
  using price_calc::models::Route;

  ExpectEqual(SplitRouteByGeoareas({}, kPolygons, kRides), {});

  Route route({
      MovementPoint(4, 6, 0, 0),   // 0 in geoarea1
      MovementPoint(5, 4, 30, 3),  // 1 in geoarea1
      MovementPoint(7, 6, 60, 6),  // 2 in geoarea1
      MovementPoint(8, 5, 80, 8)   // 3 in geoarea1 and geoarea2
  });
  ExpectEqual(SplitRouteByGeoareas(route, kPolygons, kRides),
              {RoutePart{kGeoareaName1, 0, 0, 80, 8, 0}});

  route.emplace_back(MovementPoint(11, 5, 100, 10));  // 4 in geoarea2
  ExpectEqual(SplitRouteByGeoareas(route, kPolygons, kRides),
              {RoutePart{kGeoareaName1, 0, 0, 80, 8, 0},
               RoutePart{kGeoareaName2, 80, 8, 100, 10, 4}});

  route.emplace_back(MovementPoint(10, 7, 150, 50));  // 5 in geoarea2
  ExpectEqual(SplitRouteByGeoareas(route, kPolygons, kRides),
              {RoutePart{kGeoareaName1, 0, 0, 80, 8, 0},
               RoutePart{kGeoareaName2, 80, 8, 150, 50, 4}});

  route.emplace_back(MovementPoint(8, 8, 160, 51));  // 6 in suburb
  ExpectEqual(SplitRouteByGeoareas(route, kPolygons, kRides),
              {RoutePart{kGeoareaName1, 0, 0, 80, 8, 0},
               RoutePart{kGeoareaName2, 80, 8, 160, 51, 4}});

  route.emplace_back(MovementPoint(16, 7, 200, 80));  // 7 in suburb
  ExpectEqual(SplitRouteByGeoareas(route, kPolygons, kRides),
              {RoutePart{kGeoareaName1, 0, 0, 80, 8, 0},
               RoutePart{kGeoareaName2, 80, 8, 160, 51, 4},
               RoutePart{kSuburb, 160, 51, 200, 80, 6}});

  route.emplace_back(
      MovementPoint(8.5, 5.5, 202, 83));  // 8 in geoarea1 and geoarea2
  ExpectEqual(SplitRouteByGeoareas(route, kPolygons, kRides),
              {RoutePart{kGeoareaName1, 0, 0, 80, 8, 0},
               RoutePart{kGeoareaName2, 80, 8, 160, 51, 4},
               RoutePart{kSuburb, 160, 51, 202, 83, 6}});

  route.emplace_back(MovementPoint(3, 7, 275, 130));  // 9 in geoarea1
  ExpectEqual(SplitRouteByGeoareas(route, kPolygons, kRides),
              {RoutePart{kGeoareaName1, 0, 0, 80, 8, 0},
               RoutePart{kGeoareaName2, 80, 8, 160, 51, 4},
               RoutePart{kSuburb, 160, 51, 202, 83, 6},
               RoutePart{kGeoareaName2, 202, 83, 275, 130, 8}});

  static const RouteParts kFinalRouteParts = {
      RoutePart{kGeoareaName1, 0, 0, 80, 8, 0},
      RoutePart{kGeoareaName2, 80, 8, 160, 51, 4},
      RoutePart{kSuburb, 160, 51, 202, 83, 6},
      RoutePart{kGeoareaName2, 202, 83, 275, 130, 8},
      RoutePart{kGeoareaName1, 275, 130, 400, 200, 9}};

  route.emplace_back(MovementPoint(7, 4, 400, 200));  // 10 in geoarea1
  ExpectEqual(SplitRouteByGeoareas(route, kPolygons, kRides), kFinalRouteParts);

  // test route parts caching
  RoutePartsCache route_parts_cache;

  ExpectEqual(SplitRouteByGeoareas(
                  route, kPolygons, kRides,
                  RoutePartsCachingInfo("ROUTE_ID_1", route_parts_cache)),
              kFinalRouteParts);
  EXPECT_EQ(route_parts_cache.size(), 1u);

  // different route id => must NOT take route parts from cache
  ExpectEqual(SplitRouteByGeoareas(
                  route, kPolygons, kRides,
                  RoutePartsCachingInfo("ROUTE_ID_2", route_parts_cache)),
              kFinalRouteParts);
  EXPECT_EQ(route_parts_cache.size(), 2u);

  // same set of geoarea names and route id => must take route parts from cache
  ExpectEqual(SplitRouteByGeoareas(
                  Route{}, kPolygons, kRides,
                  RoutePartsCachingInfo("ROUTE_ID_1", route_parts_cache)),
              kFinalRouteParts);
  EXPECT_EQ(route_parts_cache.size(), 2u);

  // only geoarea1 and suburb in available rides, geoarea names set will differ
  SplitRouteByGeoareas(route, kPolygons, {{kGeoareaName1, {}}, {kSuburb, {}}},
                       RoutePartsCachingInfo("ROUTE_ID_1", route_parts_cache));
  EXPECT_EQ(route_parts_cache.size(), 3u);

  // only suburb in available rides, geoarea names set will differ
  SplitRouteByGeoareas(route, kPolygons, {{kSuburb, {}}},
                       RoutePartsCachingInfo("ROUTE_ID_1", route_parts_cache));
  EXPECT_EQ(route_parts_cache.size(), 4u);
}

TEST(BaseCalcInternal, CalculatePriceForInterval) {
  using price_calc::base_calc::CalculatePriceForInterval;
  using price_calc::models::PriceInterval;
  using price_calc::models::PriceIntervals;

  PriceIntervals intervals = {PriceInterval{6, 10, 3},
                              PriceInterval{10, 20, 11},
                              PriceInterval{2, 8, 0.1}};

  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 2, intervals), 0);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 3, intervals), 0.1);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(1, 3, intervals), 0.1);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 6, intervals), 0.4);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 8, intervals), 6.6);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(6, 8, intervals), 6.2);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(6, 10, intervals), 12.2);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 10, intervals), 12.6);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 15, intervals), 67.6);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 20, intervals), 122.6);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 30, intervals), 122.6);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(25, 28, intervals), 0);

  intervals.emplace_back(
      PriceInterval{23, std::numeric_limits<double>::infinity(), 7});

  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 20, intervals), 122.6);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(0, 30, intervals), 171.6);
  EXPECT_DOUBLE_EQ(CalculatePriceForInterval(25, 28, intervals), 21);
}

namespace {

using price_calc::models::BinaryData;

std::vector<BinaryData> Serialize(
    const price_calc::base_calc::Polygons& geoareas) {
  std::vector<BinaryData> result;
  for (const auto& [geoarea_name, geoarea] : geoareas) {
    result.push_back(
        price_calc::models::serialization::Serialize(geoarea_name, geoarea));
  }
  return result;
}

RoutePartsWithPrices MakeTransfer(double distance, double time,
                                  double price_for_distance,
                                  double price_for_time) {
  const auto& kTransferRoutePartName =
      price_calc::base_calc::kTransferRoutePartName;
  RoutePartsWithPrices result;
  result.emplace_back(RoutePartWithPrices{
      RoutePart{kTransferRoutePartName, 0.0, 0.0, distance, time, 0},
      price_for_distance, price_for_time});
  return result;
}

}  // namespace

TEST(BaseCalc, Calculate) {
  using price_calc::base_calc::Calculate;
  using price_calc::base_calc::PriceAndRouteParts;
  using price_calc::base_calc::RoutePartsCache;
  using price_calc::base_calc::RoutePartsCachingInfo;
  using price_calc::models::CategoryPrices;
  using price_calc::models::CategoryPricesEx;
  using price_calc::models::MovementPoint;
  using price_calc::models::Price;
  using price_calc::models::Route;
  using price_calc::models::TransferPrices;
  using price_calc::models::WaitingPrice;

  static const WaitingPrice kWaitingPrice{std::chrono::seconds(120), 3.5};

  CategoryPricesEx prices{{111.1,
                           0.0,
                           kWaitingPrice,
                           kRides,
                           {},
                           std::nullopt,
                           std::nullopt,
                           std::nullopt},
                          std::nullopt};

  PriceAndRouteParts res_price = Calculate({}, kPolygons, prices);
  ExpectEqual(res_price, {Price(111.1, 0.0, 0.0), {}, false});

  static const Route kRoute(
      {MovementPoint(4, 6, 0, 0), MovementPoint(5, 4, 30, 3),
       MovementPoint(7, 6, 60, 6), MovementPoint(8, 5, 80, 8),
       MovementPoint(11, 5, 100, 10), MovementPoint(10, 7, 150, 50),
       MovementPoint(8, 8, 160, 51), MovementPoint(16, 7, 200, 80),
       MovementPoint(8.5, 5.5, 202, 83), MovementPoint(3, 7, 275, 130),
       MovementPoint(7, 4, 400, 200)});

  res_price = Calculate(kRoute, kPolygons, prices);
  ExpectEqual(
      res_price,
      {Price(111.1, 154.75, 53.1),
       {{{"geoarea1", 0, 0, 80, 8, 0}, 5, 0},
        {{"geoarea2", 80, 8, 160, 51, 4}, 56, 27.900000000000002},
        {{"suburb", 160, 51, 202, 83, 6}, 11.4, 0},
        {{"geoarea2", 202, 83, 275, 130, 8},
         51.099999999999994,
         19.600000000000001},
        {{"geoarea1", 275, 130, 400, 200, 9}, 31.25, 5.6000000000000005}},
       false});

  static const auto kPolygonsSerialized = Serialize(kPolygons);

  // test function, that takes in serialized data
  Price res_taximeter_price =
      Calculate(kRoute, kPolygonsSerialized,
                price_calc::models::serialization::Serialize(prices));
  ExpectEqual(res_taximeter_price, Price(111.1, 154.75, 53.1));

  prices.minimum_price = 300.0;
  res_price = Calculate(kRoute, kPolygons, prices);
  ExpectEqual(
      res_price,
      {Price(111.1, 154.75, 53.1),
       {{{"geoarea1", 0, 0, 80, 8, 0}, 5, 0},
        {{"geoarea2", 80, 8, 160, 51, 4}, 56, 27.900000000000002},
        {{"suburb", 160, 51, 202, 83, 6}, 11.4, 0},
        {{"geoarea2", 202, 83, 275, 130, 8},
         51.099999999999994,
         19.600000000000001},
        {{"geoarea1", 275, 130, 400, 200, 9}, 31.25, 5.6000000000000005}},
       false});

  prices.minimum_price = 800.0;
  res_price = Calculate(kRoute, kPolygons, prices);
  ExpectEqual(
      res_price,
      {Price(278.664367455714, 388.14861263520925, 133.18701990907664),
       {{{"geoarea1", 0, 0, 80, 8, 0}, 5, 0},
        {{"geoarea2", 80, 8, 160, 51, 4}, 56, 27.900000000000002},
        {{"suburb", 160, 51, 202, 83, 6}, 11.4, 0},
        {{"geoarea2", 202, 83, 275, 130, 8},
         51.099999999999994,
         19.600000000000001},
        {{"geoarea1", 275, 130, 400, 200, 9}, 31.25, 5.6000000000000005}},
       false});

  EXPECT_DOUBLE_EQ(res_price.price.GetTotalPrice(), 800.0);

  prices.transfer_prices = TransferPrices{
      321.5, 666.13, kWaitingPrice,
      RidePrices{
          {PriceInterval{20, kInf, 0.45}},  // 0.45 per meter from 20
          {PriceInterval{15, kInf, 0.33}}   // 0.33 per second from 15
      }};

  // check transfer with empty route and minimum_price
  res_price = Calculate({}, kPolygons, prices);
  ExpectEqual(res_price, {Price(666.13, 0.0, 0.0), {}, true});

  prices.transfer_prices->minimum_price = 0.0;
  // check transfer with empty route
  res_price = Calculate({}, kPolygons, prices);
  ExpectEqual(res_price, {Price(321.5, 0.0, 0.0), {}, true});

  res_price = Calculate(kRoute, kPolygons, prices);
  ExpectEqual(res_price, {Price(321.5, 171.0, 61.05),
                          MakeTransfer(400, 200, 171.0, 61.05), true});

  prices.transfer_prices->minimum_price = 500.0;
  res_price = Calculate(kRoute, kPolygons, prices);
  ExpectEqual(res_price, {Price(321.5, 171.0, 61.05),
                          MakeTransfer(400, 200, 171.0, 61.05), true});

  prices.transfer_prices->minimum_price = 1500.0;
  res_price = Calculate(kRoute, kPolygons, prices);
  ExpectEqual(res_price,
              {Price(871.1950140005421, 463.3727757203505, 165.43221027910758),
               MakeTransfer(400, 200, 171.0, 61.05), true});
  EXPECT_DOUBLE_EQ(res_price.price.GetTotalPrice(), 1500.0);

  // test function, that takes in serialized data and does not allow transfers
  res_taximeter_price =
      Calculate(kRoute, kPolygonsSerialized,
                price_calc::models::serialization::Serialize(prices));
  ExpectEqual(res_taximeter_price,
              Price(278.664367455714, 388.14861263520925, 133.18701990907664));
  EXPECT_DOUBLE_EQ(res_taximeter_price.GetTotalPrice(), 800.0);

  // test route parts caching
  RoutePartsCache route_parts_cache;

  prices.minimum_price = 0;
  prices.transfer_prices = std::nullopt;

  res_price = Calculate(kRoute, kPolygons, prices, true,
                        RoutePartsCachingInfo("ROUTE_ID_1", route_parts_cache));
  ExpectEqual(
      res_price,
      {Price(111.1, 154.75, 53.1),
       {{{"geoarea1", 0, 0, 80, 8, 0}, 5, 0},
        {{"geoarea2", 80, 8, 160, 51, 4}, 56, 27.900000000000002},
        {{"suburb", 160, 51, 202, 83, 6}, 11.4, 0},
        {{"geoarea2", 202, 83, 275, 130, 8},
         51.099999999999994,
         19.600000000000001},
        {{"geoarea1", 275, 130, 400, 200, 9}, 31.25, 5.6000000000000005}},
       false});
  EXPECT_EQ(route_parts_cache.size(), 1u);

  static const Route kOnePointRoute{MovementPoint(0, 0, 0, 0)};

  // same set of geoarea names and route id => must take route parts from cache
  res_price = Calculate(kOnePointRoute, kPolygons, prices, true,
                        RoutePartsCachingInfo("ROUTE_ID_1", route_parts_cache));
  ExpectEqual(
      res_price,
      {Price(111.1, 154.75, 53.1),
       {{{"geoarea1", 0, 0, 80, 8, 0}, 5, 0},
        {{"geoarea2", 80, 8, 160, 51, 4}, 56, 27.900000000000002},
        {{"suburb", 160, 51, 202, 83, 5}, 11.4, 0},
        {{"geoarea2", 202, 83, 275, 130, 8},
         51.099999999999994,
         19.600000000000001},
        {{"geoarea1", 275, 130, 400, 200, 9}, 31.25, 5.6000000000000005}},
       false});
  EXPECT_EQ(route_parts_cache.size(), 1u);

  // different set of geoarea names => must NOT take route parts from cache
  res_price =
      Calculate(kOnePointRoute, {{kGeoareaName1, kGeoarea1}}, prices, true,
                RoutePartsCachingInfo("ROUTE_ID_1", route_parts_cache));
  ExpectEqual(res_price,
              {Price(111.1, 0.0, 0.0), RoutePartsWithPrices{}, false});
  EXPECT_EQ(route_parts_cache.size(), 2u);

  // different route id => must NOT take route parts from cache
  res_price = Calculate(kOnePointRoute, kPolygons, prices, true,
                        RoutePartsCachingInfo("ROUTE_ID_2", route_parts_cache));
  ExpectEqual(res_price,
              {Price(111.1, 0.0, 0.0), RoutePartsWithPrices{}, false});
  EXPECT_EQ(route_parts_cache.size(), 3u);
}
