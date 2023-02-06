#include <gtest/gtest.h>
#include <statistics/service_metrics.hpp>
#include <userver/utils/datetime.hpp>

namespace statistics {
namespace {
const auto kNow = utils::datetime::Now();
const std::string metric("metric");

auto Time(unsigned shift) { return kNow + std::chrono::seconds(shift); }
}  // namespace

TEST(metrics, append) {
  EventQueue queue;

  queue.Append(Time(0), 1);
  ASSERT_EQ(queue.Count(), 1);
  queue.Append(Time(4), 1);
  ASSERT_EQ(queue.Count(), 2);
  queue.Append(Time(2), 1);
  queue.Append(Time(2), 1);
  ASSERT_EQ(queue.Count(), 4);
  queue.Append(Time(0), 1);
  ASSERT_EQ(queue.Count(), 5);
  queue.EraseOldEvents(Time(3));
  ASSERT_EQ(queue.Count(), 1);
}

TEST(metrics, active_counter) {
  Service service;

  ASSERT_FALSE(service.HasEvents());
  service.Append(Time(1), metric, 1);
  ASSERT_TRUE(service.HasEvents());
  service.EraseEvents(Time(0));
  ASSERT_TRUE(service.HasEvents());
  service.EraseEvents(Time(2));
  ASSERT_FALSE(service.HasEvents());

  service.EraseEvents(Time(2));
  ASSERT_FALSE(service.HasEvents());
}

TEST(metrics, erase_events) {
  Service service;

  service.Append(Time(1), "metric1", 1);
  service.Append(Time(3), "metric2", 1);

  service.EraseEvents(Time(2));
  ASSERT_TRUE(service.HasEvents());
  service.EraseEvents(Time(2));
  ASSERT_TRUE(service.HasEvents());
  service.EraseEvents(Time(2));
  ASSERT_TRUE(service.HasEvents());
}

TEST(metrics, replace_empty) {
  Service service1;
  Service service2;

  service2.Append(Time(1), metric, 1);
  ASSERT_FALSE(service1.HasEvents());
  service1.ReplaceEvents(service2);
  ASSERT_TRUE(service1.HasEvents());
  ASSERT_EQ(service1[metric].Count(), 1);
}

TEST(metrics, replace_at_front) {
  EventQueue queue1;
  EventQueue queue2;

  queue1.Append(Time(3), 1);
  queue1.Append(Time(6), 2);
  ASSERT_EQ(queue1.Count(), 3);

  queue2.Append(Time(1), 1);
  queue2.Append(Time(4), 1);
  queue2.Append(Time(3), 2);
  queue1.Replace(queue2);
  ASSERT_EQ(queue1[0].timestamp, Time(1));
  ASSERT_EQ(queue1[1].timestamp, Time(3));
  ASSERT_EQ(queue1[2].timestamp, Time(4));
  ASSERT_EQ(queue1[3].timestamp, Time(6));
  ASSERT_EQ(queue1.Count(), 6);
}

TEST(metrics, replace_existed) {
  Service service1;
  Service service2;

  service1.Append(Time(1), metric, 1);
  service1.Append(Time(1), metric, 2);
  ASSERT_EQ(service1[metric].Count(), 3);

  service2.Append(Time(1), metric, 1);
  service1.ReplaceEvents(service2);
  ASSERT_TRUE(service1.HasEvents());
  ASSERT_EQ(service1[metric].Count(), 1);
}

}  // namespace statistics
