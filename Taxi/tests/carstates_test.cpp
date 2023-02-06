#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/geofence_config.hpp>
#include <internal/carstates.hpp>
#include <models/zone.hpp>

TEST(CarStates, Empty) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  EXPECT_EQ(states.GetPendingEvents(lock), std::vector<CarZoneEvent>());
  EXPECT_EQ(states.GetAllStateEvents(lock), std::vector<CarZoneEvent>());
}

models::Zone Zone1() {
  models::Zone::polygon_t polygon;
  boost::geometry::append(polygon, Geoarea::point_t(1, 1));
  boost::geometry::append(polygon, Geoarea::point_t(1, -1));
  boost::geometry::append(polygon, Geoarea::point_t(-1, -1));
  boost::geometry::append(polygon, Geoarea::point_t(-1, 1));
  return models::Zone("1", "name", polygon);
}

TEST(CarStates, Single) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto pos1 = TrackPosition("clid", "uuid", false, 123, 0, 0);
  states.FeedCarState(pos1, std::vector<models::Zone::id_t>({"1"}), lock);

  std::vector<CarZoneEvent> events1(
      {CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                    CarZoneEvent::EventType::CarEnteredZone, 1)});
  events1[0].event_time = pos1.timestamp;

  EXPECT_EQ(states.GetPendingEvents(lock), events1);
  EXPECT_EQ(states.GetPendingEvents(lock), std::vector<CarZoneEvent>());
  EXPECT_EQ(states.GetAllStateEvents(lock), events1);
}

TEST(CarStates, BadPosition) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto pos1 = TrackPosition("clid", "uuid", true, 123, 0, 0);
  states.FeedCarState(pos1, std::vector<models::Zone::id_t>({"1"}), lock);

  std::vector<CarZoneEvent> events1({});

  EXPECT_EQ(states.GetPendingEvents(lock), events1);
  EXPECT_EQ(states.GetAllStateEvents(lock), events1);
}

TEST(CarStates, DoubleOut) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto pos1 = TrackPosition("clid", "uuid", false, 123, 0, 0);
  auto pos2 = TrackPosition("clid", "uuid", false, 124, 0, 0);
  states.FeedCarState(pos1, std::vector<models::Zone::id_t>({"1"}), lock);
  states.FeedCarState(pos2, std::vector<models::Zone::id_t>(), lock);
  // same timestamp, must be skipped
  states.FeedCarState(pos2, std::vector<models::Zone::id_t>({"1"}), lock);

  std::vector<CarZoneEvent> events1 = {
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                   CarZoneEvent::EventType::CarEnteredZone, 1),
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                   CarZoneEvent::EventType::CarLeftZone, 2)};
  events1[0].event_time = pos1.timestamp;
  events1[1].event_time = pos2.timestamp;
  std::vector<CarZoneEvent> events_all = {events1[1]};

  EXPECT_EQ(states.GetPendingEvents(lock), events1);
  EXPECT_EQ(states.GetPendingEvents(lock), std::vector<CarZoneEvent>());
  EXPECT_EQ(states.GetAllStateEvents(lock), std::vector<CarZoneEvent>());
  EXPECT_EQ(states.GetAllStateEvents(lock, false), events_all);
}

TEST(CarStates, SingleDuplicate) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto pos1 = TrackPosition("clid", "uuid", false, 123, 0, 0);
  states.FeedCarState(pos1, std::vector<models::Zone::id_t>({"1"}), lock);
  states.FeedCarState(pos1, std::vector<models::Zone::id_t>({"1"}), lock);

  std::vector<CarZoneEvent> events1 = {
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                   CarZoneEvent::EventType::CarEnteredZone, 1),
  };
  events1[0].event_time = pos1.timestamp;

  EXPECT_EQ(states.GetPendingEvents(lock), events1);
  EXPECT_EQ(states.GetAllStateEvents(lock), events1);
}

TEST(CarStates, InOkOutOutdated) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto pos1 = TrackPosition("clid", "uuid", false, 123, 0, 0);
  auto pos2 = TrackPosition("clid", "uuid", false, 120, 0, 0);
  states.FeedCarState(pos1, std::vector<models::Zone::id_t>({"1"}), lock);
  states.FeedCarState(pos2, std::vector<models::Zone::id_t>(), lock);

  std::vector<CarZoneEvent> events1 = {
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                   CarZoneEvent::EventType::CarEnteredZone, 1),
  };
  events1[0].event_time = pos1.timestamp;

  EXPECT_EQ(states.GetPendingEvents(lock), events1);
  EXPECT_EQ(states.GetAllStateEvents(lock), events1);
}

TEST(CarStates, InOutInOut) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto pos1 = TrackPosition("clid", "uuid", false, 123, 0, 0);
  auto pos2 = TrackPosition("clid", "uuid", false, 124, 0, 0);
  auto pos3 = TrackPosition("clid", "uuid", false, 125, 0, 0);
  auto pos4 = TrackPosition("clid", "uuid", false, 126, 0, 0);

  states.FeedCarState(pos1, std::vector<models::Zone::id_t>({"1"}), lock);
  states.FeedCarState(pos2, std::vector<models::Zone::id_t>(), lock);
  states.FeedCarState(pos3, std::vector<models::Zone::id_t>({"2"}), lock);
  states.FeedCarState(pos4, std::vector<models::Zone::id_t>(), lock);

  std::vector<CarZoneEvent> events1 = {
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                   CarZoneEvent::EventType::CarEnteredZone, 1),
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos2, "1"),
                   CarZoneEvent::EventType::CarLeftZone, 2),
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos3, "2"),
                   CarZoneEvent::EventType::CarEnteredZone, 3),
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos4, "2"),
                   CarZoneEvent::EventType::CarLeftZone, 4),
  };
  events1[0].event_time = pos1.timestamp;

  events1[1].state.arrival_time = pos1.timestamp;
  events1[1].state.last_update_time = pos1.timestamp;
  events1[1].event_time = pos2.timestamp;

  events1[2].event_time = pos3.timestamp;

  events1[3].state.arrival_time = pos3.timestamp;
  events1[3].state.last_update_time = pos3.timestamp;
  events1[3].event_time = pos4.timestamp;

  EXPECT_EQ(states.GetPendingEvents(lock), events1);
  EXPECT_EQ(states.GetAllStateEvents(lock), std::vector<CarZoneEvent>());
}

TEST(CarStates, FeedCarZoneEvent1) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto pos1 = TrackPosition("clid", "uuid", false, 123, 0, 0);
  auto pos2 = TrackPosition("clid", "uuid", false, 124, 0, 0);
  auto pos3 = TrackPosition("clid", "uuid", false, 125, 0, 0);
  auto pos4 = TrackPosition("clid", "uuid", false, 126, 0, 0);

  std::vector<CarZoneEvent> events1 = {
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                   CarZoneEvent::EventType::CarEnteredZone, 1)};

  std::vector<CarZoneEvent> events2 = {
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos2, "1"),
                   CarZoneEvent::EventType::CarLeftZone, 2),
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos3, "2"),
                   CarZoneEvent::EventType::CarEnteredZone, 3),
      CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos4, "2"),
                   CarZoneEvent::EventType::CarLeftZone, 4)};
  events2[0].state.arrival_time = pos1.timestamp;
  events2[2].state.arrival_time = pos3.timestamp;

  for (auto& event : events1) states.FeedCarZoneEvent(event, lock);
  // EXPECT_EQ(states.GetPendingEvents(lock), events1);
  EXPECT_EQ(states.GetAllStateEvents(lock), events1);

  for (auto& event : events2) states.FeedCarZoneEvent(event, lock);
  // EXPECT_EQ(states.GetPendingEvents(lock), events2);

  EXPECT_EQ(states.GetAllStateEvents(lock), std::vector<CarZoneEvent>());
}

TEST(CarStates, In1In2Out1Out2) {}

TEST(CarStates, InD1InD2) {}

TEST(CarStates, InD1InD2OutD1OutD2) {}

TEST(CarStates, CarLost) {
  auto docs_map = config::DocsMapForTest();
  int timeout = 10;
  const std::map<std::string, int> car_lost_timeout_by_zone = {
      {"__default__", timeout}};
  docs_map.Override("GEOFENCE_INPUT_CAR_LOST_TIMEOUT_SEC_BY_ZONE",
                    car_lost_timeout_by_zone);
  docs_map.Override("GEOFENCE_INPUT_GC_INTERVAL_SEC", timeout * 2);
  auto config_ptr = std::make_shared<config::Config>(docs_map);
  CarStates states{config_ptr};
  states.StartCarLostTracking();

  auto pos1 = TrackPosition("clid", "uuid", false, 123, 0, 0);
  auto pos2 = TrackPosition("clid2", "uuid2", false, 124 + timeout - 2, 0, 0);
  auto pos3 = TrackPosition("clid2", "uuid2", false, 124 + timeout, 0, 0);

  std::vector<CarZoneEvent> events1(
      {CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                    CarZoneEvent::EventType::CarEnteredZone, 1)});
  events1[0].event_time = pos1.timestamp;
  std::vector<CarZoneEvent> events2;
  std::vector<CarZoneEvent> events3(
      {CarZoneEvent(models::geofence::CarState::FromTrackPosition(pos1, "1"),
                    CarZoneEvent::EventType::CarLostInZone, 2)});
  events3[0].event_time = pos3.timestamp;

  auto lock = states.DoLock();
  states.FeedCarState(pos1, std::vector<models::Zone::id_t>({"1"}), lock);
  states.GarbageCollect(lock);
  EXPECT_EQ(states.GetPendingEvents(lock), events1);

  states.FeedCarState(pos2, std::vector<models::Zone::id_t>(), lock);
  states.GarbageCollect(lock);
  EXPECT_EQ(states.GetPendingEvents(lock), events2);

  states.FeedCarState(pos3, std::vector<models::Zone::id_t>(), lock);
  states.GarbageCollect(lock);
  EXPECT_EQ(states.GetPendingEvents(lock), events3);
  EXPECT_EQ(states.GetAllStateEvents(lock, false), events3);
}

bool operator!=(const CarZoneEvent& a, const CarZoneEvent& b) {
  return !(a == b);
}

TEST(CarStates, PositionFromFuture) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto t1 = time(NULL);
  auto t2 = t1 + 5000;
  auto pos = TrackPosition("clid", "uuid", false, t2, 0, 0);
  auto pos_future = pos;
  states.FeedCarState(pos, std::vector<models::Zone::id_t>({"1"}), lock);

  CarZoneEvent event_future(
      models::geofence::CarState::FromTrackPosition(pos_future, "1"),
      CarZoneEvent::EventType::CarEnteredZone, 1);

  auto events = states.GetPendingEvents(lock);
  ASSERT_EQ(events.size(), 1u);
  EXPECT_NE(events[0], event_future);

  EXPECT_LE(t1, events[0].state.arrival_time);
  EXPECT_LE(t1, events[0].state.last_update_time);
  EXPECT_GT(t1 + 2, events[0].state.arrival_time);
  EXPECT_GT(t1 + 2, events[0].state.last_update_time);

  events[0].state.arrival_time = 0;
  event_future.state.arrival_time = 0;
  events[0].state.last_update_time = 0;
  event_future.state.last_update_time = 0;

  EXPECT_LT(events[0].event_time, t1 + 2);
  EXPECT_GT(events[0].event_time, t1 - 1);

  events[0].event_time = 0;
  EXPECT_EQ(events[0], event_future);
}

TEST(CarStates, EventFromFuture) {
  CarStates states{std::make_shared<config::Config>(config::DocsMapForTest())};

  auto lock = states.DoLock();

  auto t1 = time(NULL);
  auto t2 = t1 + 5000;
  auto pos = TrackPosition("clid", "uuid", false, t2, 0, 0);
  CarZoneEvent event_future(
      models::geofence::CarState::FromTrackPosition(pos, "1"),
      CarZoneEvent::EventType::CarEnteredZone, 1);
  CarZoneEvent event = event_future;

  states.FeedCarZoneEvent(event, lock);
  auto events = states.GetAllStateEvents(lock);
  ASSERT_EQ(events.size(), 1u);
  EXPECT_NE(events[0], event_future);

  events[0].state.arrival_time = 0;
  event_future.state.arrival_time = 0;
  events[0].state.last_update_time = 0;
  event_future.state.last_update_time = 0;
  EXPECT_EQ(events[0], event_future);
}
