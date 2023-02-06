#pragma once

#include <grocery-event-bus/models/conversion.hpp>
#include <grocery-event-bus/models/topic_traits.hpp>

#include <grocery-event-bus-topics/defs/internal/test-event.hpp>

namespace grocery_event_bus::models {

namespace topics::test_event {
using Event =
    ::libraries::grocery_event_bus_topics::defs::internal::test_event::Event;

}  // namespace topics::test_event

template <>
struct TopicTrait<topics::test_event::Event> {
  constexpr static const std::string_view kName = "test-event";

  static inline std::string Serialize(const topics::test_event::Event& event) {
    return JsonSerialize(event);
  }

  static inline topics::test_event::Event Deserialize(const std::string& data) {
    return JsonDeserialize<topics::test_event::Event>(data);
  }
};

}  // namespace grocery_event_bus::models
