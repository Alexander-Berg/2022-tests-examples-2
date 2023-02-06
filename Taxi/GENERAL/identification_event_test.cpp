#include <cctv_definitions/models/identification_event.hpp>

#include <gtest/gtest.h>

namespace models {

bool operator==(const IdentificationEvent& lhs,
                const IdentificationEvent& rhs) {
  bool result = true;
  result = result && (lhs.camera_id == rhs.camera_id);
  result = result && (lhs.processor_id == rhs.processor_id);
  result = result && (lhs.person_id == rhs.person_id);
  result = result && (lhs.event_timestamp_ms == rhs.event_timestamp_ms);
  result = result && (lhs.distance == rhs.distance);
  result = result && (lhs.box.x == rhs.box.x);
  result = result && (lhs.box.y == rhs.box.y);
  result = result && (lhs.box.w == rhs.box.w);
  result = result && (lhs.box.h == rhs.box.h);
  result = result && (lhs.is_permanent_index == rhs.is_permanent_index);
  result = result && (lhs.detected_object == rhs.detected_object);
  if (lhs.frame.has_value() && rhs.frame.has_value()) {
    result = result && (*lhs.frame == *rhs.frame);
  } else {
    result = result && (!lhs.frame.has_value() && !rhs.frame.has_value());
  }
  return result;
}

}  // namespace models

TEST(IdentificationEvent, Serialization) {
  using namespace models;
  IdentificationEvent event{"processor_1", "person_1",
                            "camera_1",    "ABvvcccd+aa",
                            "ABvvcccd+aa", std::chrono::milliseconds{123456789},
                            1.44,          {10.0, 11.1, 15.2, 16.3},
                            true};
  EXPECT_EQ(
      event,
      Parse(Serialize(event, formats::serialize::To<formats::json::Value>{}),
            formats::parse::To<IdentificationEvent>{}));
}

TEST(IdentificationEvent, SerializationNoFrame) {
  using namespace models;
  IdentificationEvent event{"processor_1", "person_1",
                            "camera_1",    "ABvvcccd+aa",
                            std::nullopt,  std::chrono::milliseconds{123456789},
                            1.44,          {10.0, 11.1, 15.2, 16.3},
                            true};
  EXPECT_EQ(
      event,
      Parse(Serialize(event, formats::serialize::To<formats::json::Value>{}),
            formats::parse::To<IdentificationEvent>{}));
}
