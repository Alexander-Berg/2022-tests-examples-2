#pragma once

#include <models/booking.hpp>
#include <models/shuttle.hpp>

namespace shuttle_control::tests::helpers::interlayers {

struct ShuttleInfo {
  models::ShuttleDescriptor shuttle_desc;

  std::optional<models::StopIdT> shift_route_to;

  std::optional<models::ShuttleStatefulPosition> stateful_position;
  std::optional<::geometry::Azimuth> direction;
  std::optional<models::ShuttleStopInfo> next_stop_info;

  std::vector<models::ShortBookingInfo> bookings;

  bool operator==(const ShuttleInfo& other) const;

  friend ShuttleInfo Parse(const ::formats::json::Value& value,
                           ::formats::parse::To<ShuttleInfo>);
};

}  // namespace shuttle_control::tests::helpers::interlayers
