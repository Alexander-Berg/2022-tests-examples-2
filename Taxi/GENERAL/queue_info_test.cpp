#include "queue_info.hpp"

#include <gtest/gtest.h>

#include <clients/tracker.hpp>
#include <common/test_config.hpp>
#include <config/airport_queue_config.hpp>

std::ostream& operator<<(std::ostream& os, const std::chrono::seconds& secs) {
  return os << secs.count();
}

template <class T>
std::ostream& operator<<(std::ostream& os, const boost::optional<T>& opt) {
  if (opt)
    os << *opt;
  else
    os << "none";
  return os;
}

namespace views {
namespace queue {

const std::string kZoneId = "queue_zone";

namespace {

config::AirportQueueConfig GenerateConfig(bool show_best_place,
                                          bool show_best_waiting_time) {
  config::DocsMap docs_map = config::DocsMapForTest();
  mongo::BSONObjBuilder builder;
  builder.append("SHOW_BEST_PARKING_PLACE", show_best_place);
  builder.append("SHOW_BEST_PARKING_WAITING_TIME", show_best_waiting_time);
  docs_map.Override("AIRPORT_QUEUE_SETTINGS", BSON(kZoneId << builder.obj()));
  return *config::Config(docs_map).airport_queue_config;
}

::queue::QueuesSettings GenerateQueuesSettings(
    const config::AirportQueueConfig& config) {
  return {std::make_shared<config::AirportQueueConfig>(config),
          config.airport_queue_settings_old};
}

boost::optional<std::chrono::seconds> Seconds(int value = -1) {
  if (value < 0) return boost::none;
  return std::chrono::seconds(value);
}

}  // namespace

TEST(AirportQueueView, GetPositionOld) {
  auto cfg = GenerateConfig(false, false);
  auto queues_settings = GenerateQueuesSettings(cfg);

  // Test for empty result
  clients::tracker::DriverAirportInfo::QueueInfo queue_info;
  EXPECT_EQ(0u, GetPosition(kZoneId, queue_info, queues_settings));

  // No position, only queue count
  queue_info.queue_count = 14;
  EXPECT_EQ(14u, GetPosition(kZoneId, queue_info, queues_settings));

  // Test old position logic
  queue_info.position = 4;
  EXPECT_EQ(4u, GetPosition(kZoneId, queue_info, queues_settings));

  // Test nothing changed for old logic
  queue_info.dispatch_positions.push_back({"a", 10});
  EXPECT_EQ(4u, GetPosition(kZoneId, queue_info, queues_settings));
}

TEST(AirportQueueView, GetPositionDispatch) {
  auto cfg = GenerateConfig(true, false);
  auto queues_settings = GenerateQueuesSettings(cfg);

  // Test for empty result
  clients::tracker::DriverAirportInfo::QueueInfo queue_info;
  EXPECT_EQ(0u, GetPosition(kZoneId, queue_info, queues_settings));

  // No position, only queue count
  queue_info.queue_count = 14;
  EXPECT_EQ(14u, GetPosition(kZoneId, queue_info, queues_settings));

  // Test old position logic
  queue_info.position = 4;
  EXPECT_EQ(4u, GetPosition(kZoneId, queue_info, queues_settings));

  // Test nothing changed for old logic
  queue_info.dispatch_positions.push_back({"a", 10});
  EXPECT_EQ(10u, GetPosition(kZoneId, queue_info, queues_settings));

  queue_info.dispatch_positions.push_back({"b", 20});
  EXPECT_EQ(10u, GetPosition(kZoneId, queue_info, queues_settings));
  queue_info.dispatch_positions.push_back({"c", 5});
  EXPECT_EQ(5u, GetPosition(kZoneId, queue_info, queues_settings));
}

TEST(AirportQueueView, CheckWaitingTimeSorted) {
  auto now = utils::datetime::Now();

  models::queue::WaitingTimesIndex queue_waiting_times_index;
  std::vector<std::chrono::seconds> seconds;
  seconds.emplace_back(10);
  seconds.emplace_back(20);
  seconds.emplace_back(30);
  queue_waiting_times_index.Set(kZoneId, models::Classes::Econom, boost::none,
                                now, std::move(seconds));

  const auto& stats = queue_waiting_times_index.GetStats();
  const auto& value = stats.at(models::queue::WaitingTimesIndex::Key{
      kZoneId, models::Classes::Econom, boost::none});

  EXPECT_TRUE(value.sorted);
}

TEST(AirportQueueView, CheckWaitingTimeNotSorted) {
  auto now = utils::datetime::Now();

  models::queue::WaitingTimesIndex queue_waiting_times_index;
  std::vector<std::chrono::seconds> seconds;
  seconds.emplace_back(30);
  seconds.emplace_back(20);
  seconds.emplace_back(10);
  queue_waiting_times_index.Set(kZoneId, models::Classes::Econom, boost::none,
                                now, std::move(seconds));

  const auto& stats = queue_waiting_times_index.GetStats();
  const auto& value = stats.at(models::queue::WaitingTimesIndex::Key{
      kZoneId, models::Classes::Econom, boost::none});

  EXPECT_FALSE(value.sorted);
}

TEST(AirportQueueView, GetWaitingTimeOld) {
  auto cfg = GenerateConfig(false, false);
  auto queues_settings = GenerateQueuesSettings(cfg);
  auto now = utils::datetime::Now();

  models::queue::WaitingTimesIndex queue_waiting_times_index;
  std::vector<std::chrono::seconds> seconds;
  seconds.emplace_back(10);
  seconds.emplace_back(20);
  seconds.emplace_back(30);
  queue_waiting_times_index.Set(kZoneId, models::Classes::Econom, boost::none,
                                now, std::move(seconds));

  clients::tracker::DriverAirportInfo::QueueInfo queue_info;
  // Test for empty result
  EXPECT_EQ(Seconds(),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // Check has class only
  queue_info.class_type = models::Classes::Econom;
  EXPECT_EQ(Seconds(),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // Enable virtual
  queue_info.virtual_queue = true;
  EXPECT_EQ(Seconds(10),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // No position, only queue count
  queue_info.queue_count = 1;
  EXPECT_EQ(Seconds(20),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // Test old position logic
  queue_info.position = 0;
  EXPECT_EQ(Seconds(10),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // Test nothing changed for old logic
  queue_info.dispatch_positions.push_back({"a", 10});
  EXPECT_EQ(Seconds(10),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));
}

TEST(AirportQueueView, GetWaitingTimeDispatch) {
  auto cfg = GenerateConfig(false, true);
  auto queues_settings = GenerateQueuesSettings(cfg);
  auto now = utils::datetime::Now();

  models::queue::WaitingTimesIndex queue_waiting_times_index;
  {
    std::vector<std::chrono::seconds> seconds;
    seconds.emplace_back(10);
    seconds.emplace_back(20);
    seconds.emplace_back(30);
    seconds.emplace_back(40);
    queue_waiting_times_index.Set(kZoneId, models::Classes::Econom, boost::none,
                                  now, std::move(seconds));
  }
  {
    std::vector<std::chrono::seconds> seconds;
    seconds.emplace_back(11);
    seconds.emplace_back(21);
    seconds.emplace_back(31);
    seconds.emplace_back(41);
    queue_waiting_times_index.Set("a", models::Classes::Econom, boost::none,
                                  now, std::move(seconds));
  }
  {
    std::vector<std::chrono::seconds> seconds;
    seconds.emplace_back(12);
    seconds.emplace_back(22);
    seconds.emplace_back(32);
    seconds.emplace_back(42);
    queue_waiting_times_index.Set("b", models::Classes::Econom, boost::none,
                                  now, std::move(seconds));
  }

  clients::tracker::DriverAirportInfo::QueueInfo queue_info;
  // Test for empty result
  EXPECT_EQ(Seconds(),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // Check has class only
  queue_info.class_type = models::Classes::Econom;
  EXPECT_EQ(Seconds(),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // Enable virtual
  queue_info.virtual_queue = true;
  EXPECT_EQ(Seconds(10),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // No position, only queue count
  queue_info.queue_count = 1;
  EXPECT_EQ(Seconds(20),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  // Test old position logic
  queue_info.position = 0;
  EXPECT_EQ(Seconds(10),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  queue_info.dispatch_positions.push_back({"a", 10});
  EXPECT_EQ(Seconds(41),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  queue_info.dispatch_positions.push_back({"b", 1});
  EXPECT_EQ(Seconds(22),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  queue_info.dispatch_positions.push_back({"c", 1});
  EXPECT_EQ(Seconds(22),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));

  queue_info.dispatch_positions.clear();
  queue_info.dispatch_positions.push_back({"c", 1});
  EXPECT_EQ(Seconds(),
            GetWaitingTime(kZoneId, queue_info, queue_waiting_times_index,
                           queues_settings));
}

}  // namespace queue
}  // namespace views
