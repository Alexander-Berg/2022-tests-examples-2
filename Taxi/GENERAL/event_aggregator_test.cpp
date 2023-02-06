#include "event_aggregator.hpp"

#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

namespace {

using ::models::IdentificationEvent;
using ::models::event_history::EventAggregator;
using std::chrono::milliseconds;
const milliseconds kNewEventThreshold{10};

}  // namespace

UTEST(EventAggregatorTests, SinglePersonEvent) {
  EventAggregator aggregator(kNewEventThreshold);
  IdentificationEvent event{"processor_1", "person_1",   "camera_1",
                            "abcdABCD",    std::nullopt, milliseconds(1),
                            0.0,           {},           true};
  EXPECT_TRUE(aggregator.Push(event));
  EXPECT_FALSE(aggregator.IsEmpty());
  EXPECT_NO_THROW(aggregator.Poll());

  // the same event,
  EXPECT_FALSE(aggregator.Push(event));
  EXPECT_FALSE(aggregator.IsEmpty());
  EXPECT_NO_THROW(aggregator.Poll());

  // the same event from the past
  event.event_timestamp_ms -= milliseconds(1);
  EXPECT_FALSE(aggregator.Push(event));
  EXPECT_FALSE(aggregator.IsEmpty());
  EXPECT_NO_THROW(aggregator.Poll());

  // the person is still on the same frame
  event.event_timestamp_ms += milliseconds(2);
  EXPECT_FALSE(aggregator.Push(event));
  EXPECT_FALSE(aggregator.IsEmpty());
  EXPECT_NO_THROW(aggregator.Poll());

  // the person is back to this frame
  event.event_timestamp_ms += milliseconds(10);
  EXPECT_TRUE(aggregator.Push(event));
  EXPECT_FALSE(aggregator.IsEmpty());
  EXPECT_NO_THROW(aggregator.Poll());
}

UTEST(EventAggregatorTests, CheckDifferentPlaces) {
  EventAggregator aggregator(kNewEventThreshold);

  IdentificationEvent event{"processor_1", "person_1",   "camera_1",
                            "ABCDabcd",    std::nullopt, milliseconds(1),
                            0.0,           {},           true};
  EXPECT_TRUE(aggregator.Push(event));

  event.camera_id = "camera_2";
  EXPECT_TRUE(aggregator.Push(event));
}

UTEST(EventAggregatorTests, CheckPolling) {
  EventAggregator aggregator(kNewEventThreshold);

  const std::vector<IdentificationEvent> events{{"processor_1",
                                                 "person_1",
                                                 "camera_1",
                                                 "ABCDabcd",
                                                 std::nullopt,
                                                 milliseconds(1),
                                                 0.0,
                                                 {},
                                                 true},
                                                {"processor_1",
                                                 "person_2",
                                                 "camera_1",
                                                 "ABCDabcd",
                                                 "ABCDabcd",
                                                 milliseconds(2),
                                                 0.0,
                                                 {},
                                                 true},
                                                {"processor_1",
                                                 "person_3",
                                                 "camera_1",
                                                 "ABCDabcd",
                                                 std::nullopt,
                                                 milliseconds(3),
                                                 0.0,
                                                 {},
                                                 true},
                                                {"processor_1",
                                                 "person_4",
                                                 "camera_1",
                                                 "ABCDabcd",
                                                 "ABCDabcd",
                                                 milliseconds(4),
                                                 0.0,
                                                 {},
                                                 true}};

  std::size_t curr_size = 0;
  for (const auto& event : events) {
    EXPECT_TRUE(aggregator.Push(event));
    EXPECT_EQ(aggregator.GetSize(), ++curr_size);
  }
  IdentificationEvent threshold_event{
      "processor_1",    "person_5", "camera_1", "ABCDabcd", std::nullopt,
      milliseconds(14), 0.0,        {},         true};
  EXPECT_TRUE(aggregator.Push(threshold_event));
  EXPECT_EQ(aggregator.GetSize(), ++curr_size);
  EXPECT_NO_THROW(aggregator.Poll());
  curr_size = 1;
  EXPECT_EQ(aggregator.GetSize(), curr_size);
}

UTEST(EventAggregatorTests, CheckReset) {
  EventAggregator aggregator(kNewEventThreshold);

  const std::vector<IdentificationEvent> events{{"processor_1",
                                                 "person_1",
                                                 "camera_1",
                                                 "ABCDabcd",
                                                 std::nullopt,
                                                 milliseconds(1),
                                                 0.0,
                                                 {},
                                                 true},
                                                {"processor_1",
                                                 "person_2",
                                                 "camera_1",
                                                 "ABCDabcd",
                                                 "ABCDabcd",
                                                 milliseconds(2),
                                                 0.0,
                                                 {},
                                                 true},
                                                {"processor_1",
                                                 "person_3",
                                                 "camera_1",
                                                 "ABCDabcd",
                                                 std::nullopt,
                                                 milliseconds(3),
                                                 0.0,
                                                 {},
                                                 true},
                                                {"processor_1",
                                                 "person_4",
                                                 "camera_1",
                                                 "ABCDabcd",
                                                 "ABCDabcd",
                                                 milliseconds(4),
                                                 0.0,
                                                 {},
                                                 true}};

  std::size_t curr_size = 0;
  for (const auto& event : events) {
    EXPECT_TRUE(aggregator.Push(event));
    EXPECT_EQ(aggregator.GetSize(), ++curr_size);
  }
  aggregator.Reset();
  EXPECT_TRUE(aggregator.IsEmpty());
  curr_size = 0;
  for (const auto& event : events) {
    EXPECT_TRUE(aggregator.Push(event));
    EXPECT_EQ(aggregator.GetSize(), ++curr_size);
  }
}
