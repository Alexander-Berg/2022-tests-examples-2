#include "shuttle_info.hpp"

#include <utils/algo.hpp>

#include <tests/parsers/common.hpp>
#include <tests/parsers/models.hpp>

namespace shuttle_control::tests::helpers::interlayers {

ShuttleInfo Parse(const ::formats::json::Value& value,
                  ::formats::parse::To<ShuttleInfo>) {
  return ShuttleInfo{
      value["shuttle_desc"].As<models::ShuttleDescriptor>(),
      value["shift_route_to"].As<std::optional<models::StopIdT>>(),
      value["stateful_position"]
          .As<std::optional<models::ShuttleStatefulPosition>>(),
      utils::TransformOptional(value["direction"].As<std::optional<int16_t>>(),
                               &::geometry::Azimuth::from_value),
      value["next_stop_info"].As<std::optional<models::ShuttleStopInfo>>(),
      value["bookings"].As<std::vector<models::ShortBookingInfo>>({}),
  };
}

bool ShuttleInfo::operator==(const ShuttleInfo& other) const {
  return shuttle_desc == other.shuttle_desc &&
         shift_route_to == other.shift_route_to &&
         stateful_position == other.stateful_position &&
         direction == other.direction &&
         next_stop_info == other.next_stop_info && bookings == other.bookings;
}

}  // namespace shuttle_control::tests::helpers::interlayers
