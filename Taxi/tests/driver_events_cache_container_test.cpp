#include <gtest/gtest.h>

#include <caches/driver_events.hpp>

namespace da = ::models::dispatch::airport;

namespace {

using EventType = da::DriverEventType;
using Id = driver_id::DriverDbidUndscrUuid;
auto Time(std::time_t t) { return std::chrono::system_clock::from_time_t(t); };

caches::DriverEventsCacheContainer CreateContainer(
    const std::vector<da::DriverEvent>& events) {
  caches::DriverEventsCacheContainer container;
  for (const auto& event : events) {
    container.insert_or_assign({event.udid, event.event_id, event.event_type},
                               da::DriverEvent(event));
  }

  return container;
}

bool DriverEventComparator(const da::DriverEvent& lhs,
                           const da::DriverEvent& rhs) {
  return std::tie(lhs.udid, lhs.event_id, lhs.event_type) <
         std::tie(rhs.udid, rhs.event_id, rhs.event_type);
}

void Compare(const std::vector<da::DriverEvent>& etalon,
             const caches::DriverEventsCacheContainer& container) {
  ASSERT_EQ(etalon.size(), container.size());
  std::vector<da::DriverEvent> etalon_sorted(etalon);
  std::sort(etalon_sorted.begin(), etalon_sorted.end(), DriverEventComparator);
  std::vector<da::DriverEvent> container_sorted(container.begin(),
                                                container.end());
  std::sort(container_sorted.begin(), container_sorted.end(),
            DriverEventComparator);
  ASSERT_EQ(etalon_sorted, container_sorted);
}

void CheckGet(const caches::DriverEventsCacheContainer& container,
              const da::DriverEvent& etalon) {
  ASSERT_EQ(*container.Get({etalon.udid, etalon.event_id, etalon.event_type}),
            etalon);
}

void CheckGetNumberOfEvents(const caches::DriverEventsCacheContainer& container,
                            const std::string& driver_id,
                            const std::string& airport_id,
                            const std::unordered_set<EventType>& event_types,
                            size_t etalon) {
  ASSERT_EQ(container.GetNumberOfInterestingDriverEvents(
                Id(driver_id), airport_id, event_types),
            etalon);
}

void CheckGetNull(const caches::DriverEventsCacheContainer& container,
                  const da::DriverEvent& not_exist) {
  ASSERT_EQ(
      container.Get({not_exist.udid, not_exist.event_id, not_exist.event_type}),
      nullptr);
}

void CheckDriversOverEntryLimit(
    const caches::DriverEventsCacheContainer& container,
    const std::string& airport_id,
    const caches::DriverEventsCacheContainer::DriversOverEntryLimit& etalon) {
  const auto enter_accumulation_period = std::chrono::minutes(5);
  const size_t maximum_number_of_entries = 2;
  const auto result = container.GetDriversOverEntryLimit(
      airport_id, enter_accumulation_period, maximum_number_of_entries);
  ASSERT_EQ(result, etalon);
}

}  // namespace

TEST(DriverEventsCacheContainer, Empty) {
  caches::DriverEventsCacheContainer container;
  for ([[maybe_unused]] const auto& event : container) {
    ASSERT_TRUE(false);
  }
  ASSERT_EQ(container.size(), 0);
}

TEST(DriverEventsCacheContainer, Insert) {
  std::vector<da::DriverEvent> events = {
      {"udid1", "event_id1", EventType::kEnteredOnOrder, Id("dbid_uuid1"),
       "ekb", Time(1), std::nullopt},
      {"udid2", "event_id2", EventType::kEnteredOnOrder, Id("dbid_uuid2"),
       "ekb", Time(2), std::nullopt},

      {"udid3", "event_id3", EventType::kEnteredOnRepo, Id("dbid_uuid3"), "vko",
       Time(1), std::nullopt},
      {"udid4", "event_id4", EventType::kEnteredOnRepo, Id("dbid_uuid4"), "ekb",
       Time(3), std::nullopt},

      {"udid5", "event_id5", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid5"), "vko", Time(3), std::nullopt},
      {"udid6", "event_id6", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid6"), "ekb", Time(3), std::nullopt},
      {"udid3", "event_id3", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid3"), "vko", Time(10), std::nullopt},

      {"udid3", "event_id3_1", EventType::kEnteredMarkedArea, Id("dbid_uuid3"),
       "vko", Time(1), std::nullopt},
      {"udid3", "event_id3_2", EventType::kLeftMarkedArea, Id("dbid_uuid3"),
       "vko", Time(10), std::nullopt},
  };

  auto container = CreateContainer(events);
  Compare(events, container);

  const da::DriverEvent replaced_event = {
      "udid3",          "event_id3",   EventType::kEnteredOnRepo,
      Id("dbid_uuid3"), "new_airport", Time(123),
      std::nullopt};
  events[2] = replaced_event;
  container.insert_or_assign({"udid3", "event_id3", EventType::kEnteredOnRepo},
                             da::DriverEvent(replaced_event));
  Compare(events, container);
}

TEST(DriverEventsCacheContainer, Contains) {
  const std::vector<da::DriverEvent> events = {
      {"udid1", "event_id1", EventType::kEnteredOnOrder, Id("dbid_uuid1"),
       "ekb", Time(1), std::nullopt},
      {"udid3", "event_id3", EventType::kEnteredOnRepo, Id("dbid_uuid3"), "vko",
       Time(1), std::nullopt},
      {"udid5", "event_id5", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid5"), "vko", Time(3), std::nullopt},

      {"udid3", "event_id3_2", EventType::kLeftMarkedArea, Id("dbid_uuid3"),
       "vko", Time(10), std::nullopt},
  };
  const da::DriverEvent not_exist_event = {
      "udidXXX",          "event_idXXX", EventType::kEnteredOnRepo,
      Id("dbid_uuidXXX"), "ekb",         Time(2),
      std::nullopt};

  const auto container = CreateContainer(events);
  for (const auto& event : events) {
    ASSERT_TRUE(
        container.Contains(event.udid, event.event_id, event.event_type));
  }
  ASSERT_FALSE(container.Contains(not_exist_event.udid,
                                  not_exist_event.event_id,
                                  not_exist_event.event_type));
}

TEST(DriverEventsCacheContainer, GetEmpty) {
  caches::DriverEventsCacheContainer container;
  ASSERT_EQ(container.Get({"udid0", "event_id0", EventType::kEnteredOnOrder}),
            nullptr);
}

TEST(DriverEventsCacheContainer, Get) {
  const da::DriverEvent not_exist_event = {
      "udidXXX",           "event_idXXX", EventType::kEnteredOnRepo,
      Id("dbid_uuidXXXX"), "ekb",         Time(2),
      std::nullopt};

  const std::vector<da::DriverEvent> events = {
      {"udid1", "event_id1", EventType::kEnteredOnOrder, Id("dbid_uuid1"),
       "ekb", Time(1), std::nullopt},
      {"udid2", "event_id2", EventType::kEnteredOnOrder, Id("dbid_uuid2"),
       "ekb", Time(2), std::nullopt},

      {"udid3", "event_id3", EventType::kEnteredOnRepo, Id("dbid_uuid3"), "vko",
       Time(1), std::nullopt},
      {"udid4", "event_id4", EventType::kEnteredOnRepo, Id("dbid_uuid4"), "ekb",
       Time(3), std::nullopt},

      {"udid5", "event_id5", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid5"), "vko", Time(3), std::nullopt},
      {"udid6", "event_id6", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid6"), "ekb", Time(3), std::nullopt},
      {"udid3", "event_id3", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid3"), "vko", Time(10), std::nullopt},

      {"udid3", "event_id3_1", EventType::kEnteredMarkedArea, Id("dbid_uuid3"),
       "vko", Time(1), std::nullopt},
      {"udid3", "event_id3_2", EventType::kLeftMarkedArea, Id("dbid_uuid3"),
       "vko", Time(10), std::nullopt},
      {"udid3", "event_id3_3", EventType::kEnteredMarkedArea, Id("dbid_uuid3"),
       "vko", Time(11), std::nullopt},
  };

  const auto container = CreateContainer(events);
  CheckGet(container, events[0]);
  CheckGet(container, events[3]);
  CheckGet(container, events[6]);
  CheckGet(container, events[7]);
  CheckGet(container, events[8]);
  CheckGet(container, events[9]);
  CheckGetNull(container, not_exist_event);
}

TEST(DriverEventsCacheContainer, GetLastDriverEventEmpty) {
  caches::DriverEventsCacheContainer container;
  ASSERT_EQ(
      container.GetLastInterestingDriverEvent(
          "udid0", {EventType::kEnteredOnRepo, EventType::kEnteredMarkedArea}),
      nullptr);
}

TEST(DriverEventsCacheContainer, GetLastDriverEvent) {
  const std::string not_exist_udid = "udidXXX";

  const std::vector<da::DriverEvent> events = {
      {"udid1", "event_id1", EventType::kEnteredOnOrder, Id("dbid_uuid1"),
       "ekb", Time(1), std::nullopt},
      {"udid1", "event_id1", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid1"), "ekb", Time(3), std::nullopt},

      {"udid2", "event_id2", EventType::kEnteredOnOrder, Id("dbid_uuid2"),
       "ekb", Time(2), std::nullopt},

      {"udid3", "event_id3", EventType::kEnteredOnRepo, Id("dbid_uuid3"), "vko",
       Time(1), std::nullopt},
      {"udid3", "event_id3", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid3"), "vko", Time(10), std::nullopt},
      {"udid3", "event_id4", EventType::kEnteredOnOrder, Id("dbid_uuid3"),
       "vko", Time(15), std::nullopt},

      {"udid6", "event_id6", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid6"), "ekb", Time(3), std::nullopt},
      {"udid6", "event_id6", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid6"), "vko", Time(333), std::nullopt},
      {"udid6", "event_id6", EventType::kRelocateOfferCreated, Id("dbid_uuid6"),
       "vko", Time(80), std::nullopt},
      {"udid6", "event_id6", EventType::kRelocateOfferCreated, Id("dbid_uuid6"),
       "vko", Time(90), std::nullopt},

      // If equal time, then get first
      {"udid7", "event_id7", EventType::kEnteredOnOrder, Id("dbid_uuid7"),
       "vko", Time(100), std::nullopt},
      {"udid7", "event_id7", EventType::kEnteredOnRepo, Id("dbid_uuid7"), "vko",
       Time(100), std::nullopt},

      {"udid3", "event_id3_1", EventType::kEnteredMarkedArea, Id("dbid_uuid3"),
       "svo", Time(1), std::nullopt},

      {"udid3", "event_id3_2", EventType::kLeftMarkedArea, Id("dbid_uuid3"),
       "vko", Time(5), std::nullopt},
      {"udid3", "event_id3_3", EventType::kEnteredMarkedArea, Id("dbid_uuid3"),
       "vko", Time(10), std::nullopt},
      {"udid8", "event_id8_1", EventType::kEnteredMarkedArea, Id("dbid_uuid8"),
       "vko", Time(7), std::nullopt},
  };

  const auto container = CreateContainer(events);

  ASSERT_EQ(
      container.GetLastInterestingDriverEvent("udid6",
                                              {
                                                  EventType::kEnteredOnOrder,
                                                  EventType::kEnteredOnRepo,
                                              }),
      nullptr);
  ASSERT_EQ(*container.GetLastInterestingDriverEvent(
                "udid6",
                {
                    EventType::kEnteredOnOrder,
                    EventType::kEnteredOnRepo,
                    EventType::kRelocateOfferCreated,
                }),
            events[9]);

  ASSERT_EQ(*container.GetLastInterestingDriverEvent(
                "udid3",
                {
                    EventType::kEnteredMarkedArea,
                    EventType::kLeftMarkedArea,
                }),
            events[14]);

  ASSERT_EQ(
      container.GetLastInterestingDriverEvent(not_exist_udid,
                                              {
                                                  EventType::kEnteredOnOrder,
                                                  EventType::kEnteredOnRepo,
                                              }),
      nullptr);

  ASSERT_EQ(
      container.GetLastInterestingDriverEvent(Id("dbid_uuid6"),
                                              {
                                                  EventType::kEnteredOnOrder,
                                                  EventType::kEnteredOnRepo,
                                              }),
      nullptr);
  ASSERT_EQ(*container.GetLastInterestingDriverEvent(
                Id("dbid_uuid6"),
                {
                    EventType::kEnteredOnOrder,
                    EventType::kEnteredOnRepo,
                    EventType::kRelocateOfferCreated,
                }),
            events[9]);
  ASSERT_EQ(
      *container.GetLastInterestingDriverEvent(Id("dbid_uuid3"),
                                               {
                                                   EventType::kLeftMarkedArea,
                                               }),
      events[13]);
  ASSERT_EQ(
      *container.GetLastInterestingDriverEvent(Id("dbid_uuid3"), "vko",
                                               {
                                                   EventType::kEnteredOnRepo,
                                                   EventType::kLeftMarkedArea,
                                               }),
      events[13]);
  ASSERT_EQ(*container.GetLastInterestingDriverEvent(
                Id("dbid_uuid3"), "svo",
                {
                    EventType::kEnteredMarkedArea,
                }),
            events[12]);

  ASSERT_EQ(
      container.GetLastInterestingDriverEvent(Id("non_existing_dbid_uuid"),
                                              {
                                                  EventType::kEnteredOnOrder,
                                                  EventType::kEnteredOnRepo,
                                              }),
      nullptr);
}

TEST(DriverEventsCacheContainer, GetNumberOfEventsEmpty) {
  caches::DriverEventsCacheContainer container;
  CheckGetNumberOfEvents(container, "dbid_uuid0", "ekb",
                         {EventType::kEnteredMarkedArea}, 0);
}

TEST(DriverEventsCacheContainer, GetNumberOfEvents) {
  const std::vector<da::DriverEvent> events = {
      {"udid1", "event_id11_1", EventType::kEnteredMarkedArea, Id("dbid_uuid1"),
       "ekb", Time(1), std::nullopt},
      {"udid1", "event_id11", EventType::kEnteredOnRepo, Id("dbid_uuid1"),
       "ekb", Time(1), std::nullopt},
      {"udid1", "event_id11_3", EventType::kEnteredMarkedArea, Id("dbid_uuid1"),
       "ekb", Time(5), std::nullopt},
      {"udid1", "event_id11", EventType::kEnteredOnOrder, Id("dbid_uuid1"),
       "ekb", Time(5), std::nullopt},
      {"udid1", "event_id12_1", EventType::kEnteredMarkedArea, Id("dbid_uuid1"),
       "svo", Time(2), std::nullopt},
      {"udid1", "event_id12", EventType::kEnteredOnOrderWrongClient,
       Id("dbid_uuid1"), "svo", Time(2), std::nullopt},
      {"udid1", "event_id11_2", EventType::kLeftMarkedArea, Id("dbid_uuid1"),
       "ekb", Time(3), std::nullopt},
      {"udid1", "event_id12_2", EventType::kLeftMarkedArea, Id("dbid_uuid1"),
       "svo", Time(4), std::nullopt},

      {"udid2", "event_id21_1", EventType::kEnteredMarkedArea, Id("dbid_uuid2"),
       "ekb", Time(1), std::nullopt},
      {"udid2", "event_id21_2", EventType::kEnteredMarkedArea, Id("dbid_uuid2"),
       "ekb", Time(2), std::nullopt},
      {"udid2", "event_id21_3", EventType::kEnteredMarkedArea, Id("dbid_uuid2"),
       "ekb", Time(3), std::nullopt},

      {"udid3", "event_id31_1", EventType::kLeftMarkedArea, Id("dbid_uuid3"),
       "ekb", Time(1), std::nullopt},
      {"udid3", "event_id31_2", EventType::kLeftMarkedArea, Id("dbid_uuid3"),
       "ekb", Time(2), std::nullopt},
      {"udid3", "event_id31", EventType::kFilteredByForbiddenReason,
       Id("dbid_uuid3"), "ekb", Time(2), std::nullopt},

      {"", "event_id4", EventType::kEnteredMarkedArea, Id("dbid_uuid4"), "ekb",
       Time(2), std::nullopt}};

  const auto container = CreateContainer(events);
  //  no required events in cache
  CheckGetNumberOfEvents(
      container, "dbid_uuid11", "ekb",
      {EventType::kEnteredMarkedArea, EventType::kEnteredOnRepo}, 0);
  CheckGetNumberOfEvents(
      container, "dbid_uuid1", "spb",
      {EventType::kLeftMarkedArea, EventType::kEnteredOnRepo}, 0);
  // common case
  CheckGetNumberOfEvents(container, "dbid_uuid1", "ekb",
                         {EventType::kEnteredMarkedArea}, 2);
  CheckGetNumberOfEvents(container, "dbid_uuid1", "ekb",
                         {EventType::kLeftMarkedArea}, 1);
  CheckGetNumberOfEvents(container, "dbid_uuid1", "svo",
                         {EventType::kEnteredMarkedArea}, 1);
  CheckGetNumberOfEvents(
      container, "dbid_uuid1", "ekb",
      {EventType::kEnteredMarkedArea, EventType::kEnteredOnRepo}, 3);
  // multiple entries
  CheckGetNumberOfEvents(container, "dbid_uuid2", "ekb",
                         {EventType::kEnteredMarkedArea}, 3);
  CheckGetNumberOfEvents(container, "dbid_uuid2", "ekb",
                         {EventType::kLeftMarkedArea}, 0);
  CheckGetNumberOfEvents(container, "dbid_uuid2", "svo",
                         {EventType::kEnteredMarkedArea}, 0);
  // multiple exits
  CheckGetNumberOfEvents(container, "dbid_uuid3", "ekb",
                         {EventType::kEnteredMarkedArea}, 0);
  CheckGetNumberOfEvents(container, "dbid_uuid3", "ekb",
                         {EventType::kLeftMarkedArea}, 2);
  CheckGetNumberOfEvents(container, "dbid_uuid3", "svo",
                         {EventType::kEnteredMarkedArea}, 0);
  CheckGetNumberOfEvents(
      container, "dbid_uuid3", "ekb",
      {EventType::kLeftMarkedArea, EventType::kFilteredByForbiddenReason}, 3);
  // driver without udid
  CheckGetNumberOfEvents(container, "dbid_uuid4", "ekb",
                         {EventType::kEnteredMarkedArea}, 1);
  CheckGetNumberOfEvents(container, "dbid_uuid4", "ekb",
                         {EventType::kLeftMarkedArea}, 0);
}

TEST(DriverEventsCacheContainer, GetDriversOverEntryLimitEmpty) {
  caches::DriverEventsCacheContainer container;
  CheckDriversOverEntryLimit(container, "ekb", {});
}

TEST(DriverEventsCacheContainer, GetDriversOverEntryLimit) {
  const std::vector<da::DriverEvent> events = {
      // Not enough events to reach limit
      {"udid1", "event_id1_1", EventType::kEnteredMarkedArea, Id("dbid_uuid1"),
       "ekb", Time(150), std::nullopt},
      // Reaches limit, needs to wait 2 entry events
      {"udid2", "event_id2_1", EventType::kEnteredMarkedArea, Id("dbid_uuid2"),
       "ekb", Time(120), std::nullopt},
      {"udid2", "event_id2_2", EventType::kEnteredMarkedArea, Id("dbid_uuid2"),
       "ekb", Time(60), std::nullopt},
      {"udid2", "event_id2_3", EventType::kEnteredMarkedArea, Id("dbid_uuid2"),
       "ekb", Time(150), std::nullopt},
      // Has uninteresting events, doesn't reach limit
      {"udid3", "event_id3_1", EventType::kEnteredOnRepo, Id("dbid_uuid3"),
       "svo", Time(150), std::nullopt},
      {"udid3", "event_id3_2", EventType::kEnteredOnOrder, Id("dbid_uuid3"),
       "svo", Time(160), std::nullopt},
      {"udid3", "event_id3_3", EventType::kEnteredMarkedArea, Id("dbid_uuid3"),
       "svo", Time(170), std::nullopt},
      // Has events in both airports, reaches limit only in svo
      {"udid4", "event_id4_1", EventType::kEnteredMarkedArea, Id("dbid_uuid4"),
       "ekb", Time(299), std::nullopt},
      {"udid4", "event_id4_2", EventType::kEnteredMarkedArea, Id("dbid_uuid4"),
       "svo", Time(135), std::nullopt},
      {"udid4", "event_id4_3", EventType::kEnteredMarkedArea, Id("dbid_uuid4"),
       "svo", Time(1), std::nullopt},
      // Reaches limit in both airports,
      {"udid5", "event_id5_1", EventType::kEnteredMarkedArea, Id("dbid_uuid5"),
       "ekb", Time(100), std::nullopt},
      {"udid5", "event_id5_3", EventType::kEnteredMarkedArea, Id("dbid_uuid5"),
       "svo", Time(200), std::nullopt},
      {"udid5", "event_id5_2", EventType::kEnteredMarkedArea, Id("dbid_uuid5"),
       "svo", Time(250), std::nullopt},
      {"udid5", "event_id5_4", EventType::kEnteredMarkedArea, Id("dbid_uuid5"),
       "ekb", Time(150), std::nullopt},
  };

  const auto container = CreateContainer(events);

  CheckDriversOverEntryLimit(container, "wrong_airport", {});
  CheckDriversOverEntryLimit(
      container, "ekb",
      {{Id("dbid_uuid2"), Time(420)}, {Id("dbid_uuid5"), Time(400)}});
  CheckDriversOverEntryLimit(
      container, "svo",
      {{Id("dbid_uuid4"), Time(301)}, {Id("dbid_uuid5"), Time(500)}});
}
