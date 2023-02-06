#include "search_result_info.hpp"

#include <utils/algo.hpp>

#include <userver/formats/json/value_builder.hpp>

#include <boost/lexical_cast.hpp>
#include <boost/uuid/uuid_io.hpp>

#include <tests/parsers/common.hpp>
#include <tests/parsers/models.hpp>
#include <tests/parsers/trip_planner_operations.hpp>

namespace shuttle_control::tests::helpers::interlayers {

TripLevelResultInfo Parse(const ::formats::json::Value& value,
                          ::formats::parse::To<TripLevelResultInfo>) {
  return TripLevelResultInfo{
      boost::lexical_cast<boost::uuids::uuid>(
          value["trip_id"].As<std::string>()),
      value.As<trip_planner::operations::TripLevelResult>(),
      value["trip_route_id"].As<std::optional<models::RouteIdT>>(),
  };
}

bool TripLevelResultInfo::operator==(const TripLevelResultInfo& other) const {
  return trip_level_result == other.trip_level_result &&
         trip_route_id == other.trip_route_id;
}

ShuttleLevelResultInfo Parse(const ::formats::json::Value& value,
                             ::formats::parse::To<ShuttleLevelResultInfo>) {
  return ShuttleLevelResultInfo{
      value["shuttle_id"].As<models::ShuttleIdT>(),
      parsers::ParseToMap<
          std::unordered_map<boost::uuids::uuid, TripLevelResultInfo,
                             boost::hash<boost::uuids::uuid>>>(
          value["trips"], &TripLevelResultInfo::trip_id),
  };
}

SegmentLevelResultInfo Parse(const ::formats::json::Value& value,
                             ::formats::parse::To<SegmentLevelResultInfo>) {
  return SegmentLevelResultInfo{
      value["segment_id"].As<models::SegmentIdT>(),
      value["to_pickup"].As<std::optional<models::RouteInfo>>(),
      value["from_dropoff"].As<std::optional<models::RouteInfo>>(),
      parsers::ParseToMap<
          std::unordered_map<models::ShuttleIdT, ShuttleLevelResultInfo>>(
          value["shuttles"], &ShuttleLevelResultInfo::shuttle_id),
  };
}

RouteLevelResultInfo Parse(const ::formats::json::Value& value,
                           ::formats::parse::To<RouteLevelResultInfo>) {
  return RouteLevelResultInfo{
      value["route_id"].As<models::RouteIdT>(),
      parsers::ParseToMap<
          std::unordered_map<models::SegmentIdT, SegmentLevelResultInfo>>(
          value["segments"], &SegmentLevelResultInfo::segment_id),
  };
}

SearchResultInfo Parse(const ::formats::json::Value& value,
                       ::formats::parse::To<SearchResultInfo>) {
  return SearchResultInfo{
      value["car_ab_info"].As<std::optional<models::RouteInfo>>(),
      value["walk_ab_info"].As<std::optional<models::RouteInfo>>(),
      value["pdp_prepare_response"]
          .As<std::optional<
              clients::pricing_data_preparer::v2_prepare::post::Response>>(),
      parsers::ParseToMap<
          std::unordered_map<models::RouteIdT, RouteLevelResultInfo>>(
          value["routes"], &RouteLevelResultInfo::route_id),
  };
}

bool ShuttleLevelResultInfo::operator==(
    const ShuttleLevelResultInfo& other) const {
  return shuttle_id == other.shuttle_id && trips == other.trips;
}

bool SegmentLevelResultInfo::operator==(
    const SegmentLevelResultInfo& other) const {
  return segment_id == other.segment_id && to_pickup == other.to_pickup &&
         from_dropoff == other.from_dropoff &&
         shuttles_info == other.shuttles_info;
}

bool RouteLevelResultInfo::operator==(const RouteLevelResultInfo& other) const {
  return route_id == other.route_id && segments_info == other.segments_info;
}

bool SearchResultInfo::operator==(const SearchResultInfo& other) const {
  using OptCategories =
      std::optional<clients::pricing_data_preparer::PreparedCategories>;

  OptCategories categories = pdp_prepare_response;
  OptCategories other_categories = other.pdp_prepare_response;

  return car_ab_info == other.car_ab_info &&
         walk_ab_info == other.walk_ab_info && categories == other_categories &&
         routes_info == other.routes_info;
}

}  // namespace shuttle_control::tests::helpers::interlayers
