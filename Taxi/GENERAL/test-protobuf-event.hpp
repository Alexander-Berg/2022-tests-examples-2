#pragma once

#include <grocery_event_bus/test_protobuf_event.pb.h>

#include <grocery-event-bus/models/conversion.hpp>
#include <grocery-event-bus/models/topic_traits.hpp>

#include <grocery-event-bus-topics/defs/internal/test-protobuf-event.hpp>

namespace grocery_event_bus::models {

namespace topics::test_protobuf_event {

using Event = ::grocery_event_bus::proto::TestProtobufEvent;

}

template <>
struct TopicTrait<topics::test_protobuf_event::Event> {
  constexpr static const std::string_view kName = "test-protobuf-event";

  static inline std::string Serialize(
      const topics::test_protobuf_event::Event& event) {
    return ProtoSerialize(event);
  }

  static inline topics::test_protobuf_event::Event Deserialize(
      const std::string& data) {
    return ProtoDeserialize<topics::test_protobuf_event::Event>(data);
  }
};

}  // namespace grocery_event_bus::models
