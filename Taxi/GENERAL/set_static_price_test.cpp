#include "set_static_price.hpp"

#include <gtest/gtest.h>

#include <testing/source_path.hpp>

#include <trip-planner/operations/pricing/set_static_price_info.hpp>

#include <tests/helpers/trip_planner_operations_test_helper.hpp>

namespace {

namespace op = shuttle_control::trip_planner::operations;

const auto kMainFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/pricing/set_static_price/static_test/"
    "main.json");

const auto kNoRoute1BlockReason = ::formats::json::FromString(R"(
  {
    "reason": "no_price_info_for_route",
    "route_id": 1,
    "route_name": "route_1"
  }
)");
const auto kNoRoute2BlockReason = ::formats::json::FromString(R"(
  {
    "reason": "no_price_info_for_route",
    "route_id": 2,
    "route_name": "route_2"
  }
)");

op::pricing::SetStaticPrice CreateOperation(
    const std::string& params_json,
    const std::shared_ptr<shuttle_control::models::RoutesCacheIndex>&
        routes_cache_ptr) {
  return op::pricing::SetStaticPrice{
      op::pricing::info::kSetStaticPrice,
      ::formats::json::FromString(params_json)
          .As<op::pricing::SetStaticPrice::ParamsT>(),
      routes_cache_ptr};
}

}  // namespace

namespace shuttle_control::trip_planner::operations::pricing {

TEST(SetStaticPrice, CommonCase) {
  const auto params_json = R"(
    {
      "route_static_price_info": {
        "route_1": {
          "amount": "200.00",
          "currency": "RUB"
        },
        "route_2": {
          "amount": "10.00",
          "currency": "EUR"
        }
      }
    }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto& route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  CreateOperation(params_json, route_cache_ptr)
      .Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::pair<models::PriceData, models::PriceData>,
                     boost::hash<boost::uuids::uuid>>
      expected_prices{
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b1"),
              {
                  models::PriceData{models::MoneyType("200.00"), "RUB"},
                  models::PriceData{models::MoneyType("400.00"), "RUB"},
              },
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b2"),
              {
                  models::PriceData{models::MoneyType("200.00"), "RUB"},
                  models::PriceData{models::MoneyType("400.00"), "RUB"},
              },
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b3"),
              {
                  models::PriceData{models::MoneyType("10.00"), "EUR"},
                  models::PriceData{models::MoneyType("20.00"), "EUR"},
              },
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b4"),
              {
                  models::PriceData{models::MoneyType("10.00"), "EUR"},
                  models::PriceData{models::MoneyType("20.00"), "EUR"},
              },
          },
      };

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          const auto& it = expected_prices.find(trip_id);
          EXPECT_FALSE(it == expected_prices.end());
          const auto& [per_seat_price, total_price] = it->second;

          EXPECT_TRUE(trip_level.per_seat_price.has_value());
          EXPECT_TRUE(trip_level.total_price.has_value());

          EXPECT_EQ(per_seat_price, trip_level.per_seat_price.value());
          EXPECT_EQ(total_price, trip_level.total_price.value());

          EXPECT_TRUE(trip_level.skip_reasons.empty());

          expected_prices.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_prices.empty());
}

TEST(SetStaticPrice, MissingRouteData) {
  const auto params_json = R"(
    {
      "route_static_price_info": {}
    }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto& route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  CreateOperation(params_json, route_cache_ptr)
      .Process(search_query, search_result);

  std::unordered_map<std::string, ::formats::json::Value> route1_block_reasons{
      {"set_static_price", kNoRoute1BlockReason},
  };
  std::unordered_map<std::string, ::formats::json::Value> route2_block_reasons{
      {"set_static_price", kNoRoute2BlockReason},
  };
  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          EXPECT_FALSE(trip_level.per_seat_price.has_value());
          EXPECT_FALSE(trip_level.total_price.has_value());

          if (route_id == models::RouteIdT{1}) {
            EXPECT_EQ(trip_level.skip_reasons, route1_block_reasons);
          } else if (route_id == models::RouteIdT{2}) {
            EXPECT_EQ(trip_level.skip_reasons, route2_block_reasons);
          } else {
            FAIL() << "unreachable";
          }
        }
      }
    }
  }
}

}  // namespace shuttle_control::trip_planner::operations::pricing
