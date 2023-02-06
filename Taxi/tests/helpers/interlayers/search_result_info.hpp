#pragma once

#include <trip-planner/operations/search_result.hpp>

namespace shuttle_control::tests::helpers::interlayers {

struct TripLevelResultInfo {
  boost::uuids::uuid trip_id;
  trip_planner::operations::TripLevelResult trip_level_result;
  std::optional<models::RouteIdT> trip_route_id;
  bool operator==(const TripLevelResultInfo& other) const;

  friend TripLevelResultInfo Parse(const ::formats::json::Value& value,
                                   ::formats::parse::To<TripLevelResultInfo>);
};

struct ShuttleLevelResultInfo {
  models::ShuttleIdT shuttle_id;

  std::unordered_map<boost::uuids::uuid, TripLevelResultInfo,
                     boost::hash<boost::uuids::uuid>>
      trips;

  bool operator==(const ShuttleLevelResultInfo& other) const;

  friend ShuttleLevelResultInfo Parse(
      const ::formats::json::Value& value,
      ::formats::parse::To<ShuttleLevelResultInfo>);
};

struct SegmentLevelResultInfo {
  models::SegmentIdT segment_id;

  std::optional<models::RouteInfo> to_pickup;
  std::optional<models::RouteInfo> from_dropoff;

  std::unordered_map<models::ShuttleIdT, ShuttleLevelResultInfo> shuttles_info;

  bool operator==(const SegmentLevelResultInfo& other) const;

  friend SegmentLevelResultInfo Parse(
      const ::formats::json::Value& value,
      ::formats::parse::To<SegmentLevelResultInfo>);
};

struct RouteLevelResultInfo {
  models::RouteIdT route_id;

  std::unordered_map<models::SegmentIdT, SegmentLevelResultInfo> segments_info;

  bool operator==(const RouteLevelResultInfo& other) const;

  friend RouteLevelResultInfo Parse(const ::formats::json::Value& value,
                                    ::formats::parse::To<RouteLevelResultInfo>);
};

struct SearchResultInfo {
  std::optional<models::RouteInfo> car_ab_info;
  std::optional<models::RouteInfo> walk_ab_info;
  std::optional<clients::pricing_data_preparer::v2_prepare::post::Response>
      pdp_prepare_response;

  std::unordered_map<models::RouteIdT, RouteLevelResultInfo> routes_info;

  bool operator==(const SearchResultInfo& other) const;

  friend SearchResultInfo Parse(const ::formats::json::Value& value,
                                ::formats::parse::To<SearchResultInfo>);
};

}  // namespace shuttle_control::tests::helpers::interlayers
