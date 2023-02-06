#pragma once

#include <grocery-event-bus/models/conversion.hpp>
#include <grocery-event-bus/models/topic_traits.hpp>

#include <grocery-event-bus-topics/defs/internal/test-bulk-event.hpp>

namespace grocery_event_bus::models {

namespace topics::test_bulk_event {
using Event = ::libraries::grocery_event_bus_topics::defs::internal::
    test_bulk_event::Event;

}  // namespace topics::test_bulk_event

template <>
struct TopicTrait<topics::test_bulk_event::Event> {
  constexpr static const std::string_view kName = "test-bulk-event";

  static inline std::string Serialize(
      const topics::test_bulk_event::Event& event) {
    return JsonSerialize(event);
  }

  static inline topics::test_bulk_event::Event Deserialize(
      const std::string& data) {
    return JsonDeserialize<topics::test_bulk_event::Event>(data);
  }
};

}  // namespace grocery_event_bus::models
