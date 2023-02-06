#include "models.hpp"

#include <boost/lexical_cast.hpp>

#include <models/booking.hpp>
#include <models/pause_state.hpp>
#include <models/routes_cache.hpp>
#include <models/routing.hpp>
#include <models/shuttle.hpp>
#include <utils/algo.hpp>

#include <tests/parsers/common.hpp>

namespace models {

DbidUuid Parse(const ::formats::json::Value& value,
               formats::parse::To<DbidUuid>) {
  return DbidUuid{
      value["park_id"].As<std::string>(),
      value["driver_profile_id"].As<std::string>(),
  };
}

}  // namespace models

namespace shuttle_control::models {

RouteInfo Parse(const ::formats::json::Value& value,
                formats::parse::To<RouteInfo>) {
  return RouteInfo{
      value["time"].As<std::chrono::seconds>(),
      value["distance"].As<double>(),
      value["timestamp"].As<std::chrono::system_clock::time_point>(),
  };
}

SegmentIdT Parse(const ::formats::json::Value& value,
                 formats::parse::To<SegmentIdT>) {
  return SegmentIdT{
      value["begin"].As<StopIdT>(),
      value["end"].As<StopIdT>(),
  };
}

ShuttleDescriptor Parse(const ::formats::json::Value& value,
                        formats::parse::To<ShuttleDescriptor>) {
  return ShuttleDescriptor{
      value["driver_id"].As<::models::DbidUuid>(),
      value["shuttle_id"].As<ShuttleIdT>(),
      value["route_id"].As<RouteIdT>(),
      value["capacity"].As<int32_t>(16),
      value["revision"].As<int64_t>(1),
      value["drw_state"].As<DRWState>(DRWState::Disabled),
      value["started_at"]
          .As<std::optional<std::chrono::system_clock::time_point>>(),
      value["ended_at"]
          .As<std::optional<std::chrono::system_clock::time_point>>(),
      value["ticket_length"].As<int32_t>(4),
      value["ticket_check_enabled"].As<bool>(false),
      value["use_external_confirmation_code"].As<bool>(false),
      value["work_mode"].As<WorkModeType>(WorkModeType::kShuttle),
      utils::TransformOptional(
          value["workshift_id"].As<std::optional<std::string>>(),
          &boost::lexical_cast<boost::uuids::uuid, std::string>),
      value["shift_subscription_id"].As<std::optional<int64_t>>(),
      value["view_id"]
          .As<std::optional<shuttle_control::models::RouteViewIdT>>(),
      value["vfh_id"].As<std::optional<std::string>>(),
      value["remaining_pauses"].As<int32_t>(),
      value["pause_state"].As<PauseState>(),
      value["pause_id"].As<std::optional<PauseIdT>>(),
  };
}

DRWState Parse(const ::formats::json::Value& value,
               formats::parse::To<DRWState>) {
  const auto& str_value = value.As<std::string>();
  if (str_value == "assigned") {
    return DRWState::Assigned;
  } else if (str_value == "active") {
    return DRWState::Active;
  } else if (str_value == "disabled") {
    return DRWState::Disabled;
  } else if (str_value == "disabled_active") {
    return DRWState::DisabledActive;
  } else {
    throw formats::json::ParseException(
        "Value of '" + value.GetPath() + "' (" + str_value +
        ") is not parseable into DRWState enum. Use lower snake case");
  }
}

WorkModeType Parse(const ::formats::json::Value& value,
                   formats::parse::To<WorkModeType>) {
  const auto& str_value = value.As<std::string>();
  if (str_value == "shuttle") {
    return WorkModeType::kShuttle;
  } else if (str_value == "shuttle_fix") {
    return WorkModeType::kShuttleFix;
  } else {
    throw formats::json::ParseException(
        "Value of '" + value.GetPath() + "' (" + str_value +
        ") is not parseable into WorkModeType enum. Use lower snake case");
  }
}

Route Parse(const ::formats::json::Value& value, formats::parse::To<Route>) {
  Route route{tests::parsers::ParseToRouteMeta(value["meta"])};

  const auto& json_points =
      value["points"].As<std::vector<formats::json::Value>>();

  for (const auto& json_point : json_points) {
    Route::ViaPoint via_point{
        json_point["point_id"].As<PointIdT>(),
        tests::parsers::ParseToPosition(json_point["position"]),
        json_point["is_anchor"].As<bool>(),
    };

    if (json_point.HasMember("stop_id")) {
      Route::StopPoint stop_point{std::move(via_point),
                                  json_point["stop_id"].As<StopIdT>(),
                                  json_point["name"].As<std::string>(),
                                  json_point["is_terminal"].As<bool>(false),
                                  {}};
      route.AddStopPoint(std::move(stop_point));
    } else {
      route.AddViaPoint(std::move(via_point));
    }
  }

  return route;
}

ShuttleStatefulPosition Parse(const ::formats::json::Value& value,
                              formats::parse::To<ShuttleStatefulPosition>) {
  return ShuttleStatefulPosition{
      value["route_position"].As<ShuttleEnRoutePosition>(),
      value["state"].As<ShuttleTripState>(),
  };
}

ShuttleEnRoutePosition Parse(const ::formats::json::Value& value,
                             formats::parse::To<ShuttleEnRoutePosition>) {
  return ShuttleEnRoutePosition{
      tests::parsers::ParseToRouteIndexSegment<PointIdT>(
          value["cur_point_segment"]),
      tests::parsers::ParseToRouteIndexSegment<StopIdT>(
          value["cur_stop_segment"]),
      tests::parsers::ParseToPosition(value["position"]),
  };
}

ShuttleTripState Parse(const ::formats::json::Value& value,
                       formats::parse::To<ShuttleTripState>) {
  return ShuttleTripState{
      value["current_lap"].As<ShuttleLapT>(),
      value["begin_stop_id"].As<StopIdT>(),
      value["next_stop_id"].As<StopIdT>(),
      std::nullopt,
      std::nullopt,
      value["updated_at"].As<std::chrono::system_clock::time_point>(),
      utils::TransformOptional(
          value["average_speed"].As<std::optional<double>>(),
          &KmHSpeed::from_value),
      value["advanced_at"].As<std::chrono::system_clock::time_point>(),
      value["block_reason"].As<DriverBlockReason>(),
      value["processed_at"].As<std::chrono::system_clock::time_point>(),
  };
}

DriverBlockReason Parse(const ::formats::json::Value& value,
                        formats::parse::To<DriverBlockReason>) {
  const auto& str_value = value.As<std::string>();
  if (str_value == "None") {
    return DriverBlockReason::kNone;
  } else if (str_value == "NotOnRoute") {
    return DriverBlockReason::kNotOnRoute;
  } else if (str_value == "Immobility") {
    return DriverBlockReason::kImmobility;
  } else if (str_value == "OutOfWorkshift") {
    return DriverBlockReason::kOutOfWorkshift;
  } else {
    throw formats::json::ParseException("Value of '" + value.GetPath() + "' (" +
                                        str_value +
                                        ") is not parseable into enum");
  }
}

ShortBookingInfo Parse(const ::formats::json::Value& value,
                       formats::parse::To<ShortBookingInfo>) {
  return ShortBookingInfo{
      boost::lexical_cast<boost::uuids::uuid>(
          value["booking_id"].As<std::string>()),
      value["status"].As<BookingStatus>(),
      value["booked_segment"].As<BookedSeatSegment>(),
      value["pickup_timestamp"]
          .As<std::optional<std::chrono::system_clock::time_point>>(),
      value["dropoff_timestamp"]
          .As<std::optional<std::chrono::system_clock::time_point>>(),
      value["created_at"].As<std::chrono::system_clock::time_point>(),
      value["picked_up_at"]
          .As<std::optional<std::chrono::system_clock::time_point>>()};
}

BookedSeatSegment Parse(const ::formats::json::Value& value,
                        formats::parse::To<BookedSeatSegment>) {
  return BookedSeatSegment{
      boost::lexical_cast<boost::uuids::uuid>(
          value["booking_id"].As<std::string>()),
      value["pickup_stop_id"].As<StopIdT>(),
      value["dropoff_stop_id"].As<StopIdT>(),
      value["pickup_lap"].As<StopLapT>(),
      value["dropoff_lap"].As<StopLapT>(),
  };
}

ShuttleStopInfo Parse(const ::formats::json::Value& value,
                      formats::parse::To<ShuttleStopInfo>) {
  return ShuttleStopInfo{
      value["stop_id"].As<StopIdT>(),
      value["lap"].As<StopLapT>(),
  };
}

ShuttleLoad Parse(const ::formats::json::Value& value,
                  formats::parse::To<ShuttleLoad>) {
  return ShuttleLoad{
      value["seats_available"].As<int64_t>(),
      value["seats_taken"].As<int64_t>(),
  };
}

PriceData Parse(const ::formats::json::Value& value,
                formats::parse::To<PriceData>) {
  return PriceData{
      value["amount"].As<MoneyType>(),
      value["currency"].As<std::string>(),
  };
}

GeoData Parse(const ::formats::json::Value& value,
              formats::parse::To<GeoData>) {
  return GeoData{
      value["timezone"].As<std::optional<std::string>>(),
      value["city"].As<std::optional<std::string>>(),
      value["tariff_zone"].As<std::optional<std::string>>(),
  };
}

PauseState Parse(const ::formats::json::Value& value,
                 formats::parse::To<PauseState>) {
  const auto& str_value = value.As<std::string>();
  if (str_value == "inactive") {
    return PauseState::kInactive;
  } else if (str_value == "requested") {
    return PauseState::kRequested;
  } else if (str_value == "in_work") {
    return PauseState::kInWork;
  } else {
    throw formats::json::ParseException(
        "Value of '" + value.GetPath() + "' (" + str_value +
        ") is not parseable into PauseState enum. Use lower snake case");
  }
}

}  // namespace shuttle_control::models
