#include "trip_planner_operations.hpp"

#include <boost/lexical_cast.hpp>

#include <trip-planner/operations/search_query.hpp>
#include <trip-planner/operations/search_result.hpp>
#include <utils/algo.hpp>

#include <tests/parsers/common.hpp>
#include <tests/parsers/models.hpp>

namespace {

const auto kAppPlatformDefault = "unittests";
const auto kAppVersionDefault = "1.1.1";

}  // namespace

namespace shuttle_control::trip_planner::operations {

SearchQuery Parse(const ::formats::json::Value& value,
                  formats::parse::To<SearchQuery>) {
  return SearchQuery{
      value["app_platform"].As<std::string>(kAppPlatformDefault),
      value["app_version"].As<std::string>(kAppVersionDefault),
      tests::parsers::ParseToPosition(value["from"]),
      tests::parsers::ParseToPosition(value["to"]),
      value["tariff_zone"].As<std::string>(),
      value["passengers_count"].As<int32_t>(),
      value["payment_type"].As<std::optional<::handlers::PaymentType>>(),
      value["payment_method_id"].As<std::optional<std::string>>(),
      value["yandex_uid"].As<std::optional<std::string>>(),
      value["origin_service_id"].As<std::optional<std::string>>(),
      value["external_confirmation_code"].As<std::optional<std::string>>(),
      value["external_passenger_id"].As<std::optional<std::string>>(),
      value["phone_id"].As<std::optional<std::string>>()};
}

TripLevelResult Parse(const ::formats::json::Value& value,
                      formats::parse::To<TripLevelResult>) {
  return TripLevelResult{
      boost::lexical_cast<boost::uuids::uuid>(
          value["trip_id"].As<std::string>()),
      value["pickup_stop_info"].As<models::ShuttleStopInfo>(),
      value["dropoff_stop_info"].As<models::ShuttleStopInfo>(),
      value["trip_route"].As<std::optional<models::Route>>(),
      value["next_trip_stop_info"].As<std::optional<models::ShuttleStopInfo>>(),
      value["shuttle_load"].As<models::ShuttleLoad>(),
      value["eta_at_pickup"].As<std::optional<models::RouteInfo>>(),
      value["route_info"].As<std::optional<models::RouteInfo>>(),
      value["per_seat_price"].As<std::optional<models::PriceData>>(),
      value["total_price"].As<std::optional<models::PriceData>>(),
      value["score"].As<std::optional<int32_t>>(),
      value["skip_reasons"]
          .As<std::unordered_map<std::string, ::formats::json::Value>>({}),
  };
}

}  // namespace shuttle_control::trip_planner::operations
