#include <chrono>
#include <models/wms_shifts.hpp>
#include <userver/utest/utest.hpp>
#include "helpers/shifts.hpp"

using CourierId = grocery_checkins::models::CourierId;
using CouriersShiftsIndex =
    grocery_checkins::models::wms::ShiftsIndex::PerformersIndex;
using ShiftStatus = grocery_checkins::models::ShiftStatus;
using WmsShift = grocery_checkins::models::wms::Shift;

using grocery_checkins::helpers::FindUpdatedShifts;

using optional_timepoint = std::optional<std::chrono::system_clock::time_point>;
using namespace std::chrono_literals;

auto collect = [](std::vector<WmsShift>& shifts) mutable {
  shifts.clear();
  return [&shifts](const WmsShift& shift) { shifts.push_back(shift); };
};

auto find = [](const auto& shifts, std::string courier_id) {
  CourierId id{std::move(courier_id)};
  return std::find_if(shifts.begin(), shifts.end(),
                      [&id](const WmsShift& shift) {
                        return shift.courier_id == id;
                      }) != shifts.end();
};
auto dummy = [](const WmsShift&) {};
CouriersShiftsIndex null_index_ptr{};
grocery_shared::LegacyDepotId depot_id{"depot_id"};

UTEST(EventNotificatorTestSuite, FindNewShiftsDiff) {
  auto now = ::utils::datetime::Now();

  // Fill the shifts from start
  CourierId cid1{"c1"};
  CourierId cid2{"c2"};
  CourierId cid3{"c3"};
  CourierId cid4{"c4"};

  std::vector<WmsShift> fetched_shifts = {
      WmsShift{cid1, "s1", depot_id, now, optional_timepoint(),
               ShiftStatus::kInProgress},
      WmsShift{cid2, "s2", depot_id, now, optional_timepoint(),
               ShiftStatus::kClosed},
      WmsShift{cid3, "s3", depot_id, now, optional_timepoint(),
               ShiftStatus::kPaused},
      WmsShift{cid4, "s4", depot_id, now + 10min, optional_timepoint(),
               ShiftStatus::kInProgress}};

  // Prepare internal structures
  //  SavedCache saved_cache;
  std::vector<WmsShift> new_shifts;
  std::vector<WmsShift> empty_fetched_shifts{};

  // Test 1:  Check if empty cache doesn't break anything
  FindUpdatedShifts(empty_fetched_shifts, null_index_ptr, collect(new_shifts),
                    dummy, dummy, dummy);
  ASSERT_EQ(new_shifts.size(), 0);

  // Test 2: check that from start, it can find all valid caches
  FindUpdatedShifts(fetched_shifts, null_index_ptr, collect(new_shifts), dummy,
                    dummy, dummy);
  ASSERT_EQ(new_shifts.size(), 2);
  ASSERT_TRUE(find(new_shifts, "c1"));
  ASSERT_FALSE(find(new_shifts, "c2"));
  ASSERT_TRUE(find(new_shifts, "c3"));
  ASSERT_FALSE(find(new_shifts, "c4"));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c1;
  shifts_map_c1.TryAddShift(std::make_shared<WmsShift>(
      WmsShift{cid1, "s1", depot_id, now, optional_timepoint(),
               ShiftStatus::kInProgress}));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c2;
  shifts_map_c2.TryAddShift(std::make_shared<WmsShift>(WmsShift{
      cid2, "s2", depot_id, now, optional_timepoint(), ShiftStatus::kClosed}));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c3;
  shifts_map_c3.TryAddShift(std::make_shared<WmsShift>(WmsShift{
      cid3, "s3", depot_id, now, optional_timepoint(), ShiftStatus::kPaused}));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c4;
  shifts_map_c4.TryAddShift(std::make_shared<WmsShift>(
      WmsShift{cid4, "s4", depot_id, now + 10min, optional_timepoint(),
               ShiftStatus::kInProgress}));

  CouriersShiftsIndex old_shifts_index = {
      {cid1, shifts_map_c1},
      {cid2, shifts_map_c2},
      {cid3, shifts_map_c3},
      {cid4, shifts_map_c4},
  };

  // Test 2: it should find any new shifts on the old data
  FindUpdatedShifts(fetched_shifts, old_shifts_index, collect(new_shifts),
                    dummy, dummy, dummy);
  ASSERT_EQ(new_shifts.size(), 0);

  // Test 3: change the status and find out if this shift will be found
  fetched_shifts[0].status = ShiftStatus::kPaused;
  fetched_shifts[2].status = ShiftStatus::kInProgress;
  FindUpdatedShifts(fetched_shifts, old_shifts_index, collect(new_shifts),
                    dummy, dummy, dummy);
  ASSERT_EQ(new_shifts.size(), 0);

  grocery_checkins::models::wms::ShiftsMap shifts_map_c1_new;
  shifts_map_c1_new.TryAddShift(std::make_shared<WmsShift>(fetched_shifts[0]));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c3_new;
  shifts_map_c3_new.TryAddShift(std::make_shared<WmsShift>(fetched_shifts[2]));

  CouriersShiftsIndex old_shifts_index_updated = {
      {cid1, shifts_map_c1_new},
      {cid2, shifts_map_c2},
      {cid3, shifts_map_c3_new},
      {cid4, shifts_map_c4},
  };

  // Test 4: Add new shift
  CourierId cid5{"c5"};
  fetched_shifts.push_back(WmsShift{cid5, "s5", depot_id, now,
                                    optional_timepoint(),
                                    ShiftStatus::kInProgress});
  FindUpdatedShifts(fetched_shifts, old_shifts_index_updated,
                    collect(new_shifts), dummy, dummy, dummy);
  ASSERT_EQ(new_shifts.size(), 1);
  ASSERT_TRUE(find(new_shifts, "c5"));
}

UTEST(EventNotificatorTestSuite, FindPausedUnpausedShiftsDiff) {
  auto now = ::utils::datetime::Now();

  // Fill the shifts from start
  CourierId cid1{"c1"};
  CourierId cid2{"c2"};

  std::vector<WmsShift> fetched_shifts = {
      WmsShift{cid1, "s1", depot_id, now, optional_timepoint(),
               ShiftStatus::kPaused},
      WmsShift{cid2, "s2", depot_id, now, optional_timepoint(),
               ShiftStatus::kInProgress}};

  // Prepare internal structures
  std::vector<WmsShift> new_shifts;
  std::vector<WmsShift> paused_shifts;
  std::vector<WmsShift> unpaused_shifts;

  // Test new with paused
  FindUpdatedShifts(fetched_shifts, null_index_ptr, collect(new_shifts), dummy,
                    collect(paused_shifts), dummy);

  ASSERT_EQ(new_shifts.size(), 2);
  ASSERT_EQ(paused_shifts.size(), 1);
  ASSERT_TRUE(find(new_shifts, "c1"));
  ASSERT_TRUE(find(new_shifts, "c2"));
  ASSERT_TRUE(find(paused_shifts, "c1"));
  ASSERT_FALSE(find(paused_shifts, "c2"));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c1;
  shifts_map_c1.TryAddShift(std::make_shared<WmsShift>(WmsShift{
      cid1, "s1", depot_id, now, optional_timepoint(), ShiftStatus::kPaused}));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c2;
  shifts_map_c2.TryAddShift(std::make_shared<WmsShift>(
      WmsShift{cid2, "s2", depot_id, now, optional_timepoint(),
               ShiftStatus::kInProgress}));

  CouriersShiftsIndex old_shifts_index = {
      {cid1, shifts_map_c1},
      {cid2, shifts_map_c2},
  };

  // Test in_progress -> paused
  new_shifts.clear();
  fetched_shifts[1] = WmsShift{
      cid2, "s2", depot_id, now, optional_timepoint(), ShiftStatus::kPaused};

  FindUpdatedShifts(fetched_shifts, old_shifts_index, collect(new_shifts),
                    dummy, collect(paused_shifts), dummy);
  ASSERT_EQ(new_shifts.size(), 0);
  ASSERT_EQ(paused_shifts.size(), 2);
  ASSERT_TRUE(find(paused_shifts, "c2"));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c2_new;
  shifts_map_c2_new.TryAddShift(std::make_shared<WmsShift>(WmsShift{
      cid2, "s2", depot_id, now, optional_timepoint(), ShiftStatus::kPaused}));

  CouriersShiftsIndex old_shifts_index_updated = {
      {cid1, shifts_map_c1},
      {cid2, shifts_map_c2_new},
  };

  // Test paused -> in_progress
  new_shifts.clear();
  paused_shifts.clear();
  fetched_shifts[0] = WmsShift{cid1,
                               "s1",
                               depot_id,
                               now,
                               optional_timepoint(),
                               ShiftStatus::kInProgress};

  FindUpdatedShifts(fetched_shifts, old_shifts_index_updated, dummy, dummy,
                    dummy, collect(unpaused_shifts));
  ASSERT_EQ(new_shifts.size(), 0);
  ASSERT_EQ(paused_shifts.size(), 0);
  ASSERT_EQ(unpaused_shifts.size(), 1);
  ASSERT_TRUE(find(unpaused_shifts, "c1"));
}

UTEST(EventNotificatorTestSuite, FindClosedShiftsDiff) {
  auto now = ::utils::datetime::Now();

  // Fill the shifts from start
  CourierId cid1{"c1"};
  CourierId cid2{"c2"};
  CourierId cid3{"c3"};

  std::vector<WmsShift> fetched_shifts = {
      WmsShift{cid1, "s1", depot_id, now, optional_timepoint(),
               ShiftStatus::kInProgress},
      WmsShift{cid2, "s2", depot_id, now, optional_timepoint(),
               ShiftStatus::kPaused},
      WmsShift{cid3, "s3", depot_id, now, optional_timepoint(),
               ShiftStatus::kClosed}};

  // Prepare internal structures
  std::vector<WmsShift> new_shifts;
  std::vector<WmsShift> paused_shifts;
  std::vector<WmsShift> closed_shifts;

  // Test new with paused
  FindUpdatedShifts(fetched_shifts, null_index_ptr, collect(new_shifts), dummy,
                    collect(paused_shifts), dummy);

  ASSERT_EQ(new_shifts.size(), 2);
  ASSERT_EQ(paused_shifts.size(), 1);
  ASSERT_TRUE(find(new_shifts, "c1"));
  ASSERT_TRUE(find(new_shifts, "c2"));
  ASSERT_TRUE(find(paused_shifts, "c2"));
  ASSERT_FALSE(find(paused_shifts, "c1"));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c1;
  shifts_map_c1.TryAddShift(std::make_shared<WmsShift>(
      WmsShift{cid1, "s1", depot_id, now, optional_timepoint(),
               ShiftStatus::kInProgress}));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c2;
  shifts_map_c2.TryAddShift(std::make_shared<WmsShift>(WmsShift{
      cid2, "s2", depot_id, now, optional_timepoint(), ShiftStatus::kPaused}));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c3;
  shifts_map_c3.TryAddShift(std::make_shared<WmsShift>(WmsShift{
      cid3, "s3", depot_id, now, optional_timepoint(), ShiftStatus::kClosed}));

  CouriersShiftsIndex old_shifts_index = {
      {cid1, shifts_map_c1},
      {cid2, shifts_map_c2},
      {cid3, shifts_map_c3},
  };

  // Test in_progress and paused -> closed
  new_shifts.clear();
  fetched_shifts[0] = WmsShift{
      cid1, "s1", depot_id, now, optional_timepoint(), ShiftStatus::kClosed};
  fetched_shifts[1] = WmsShift{
      cid2, "s2", depot_id, now, optional_timepoint(), ShiftStatus::kClosed};

  FindUpdatedShifts(fetched_shifts, old_shifts_index, collect(new_shifts),
                    collect(closed_shifts), collect(paused_shifts), dummy);
  ASSERT_EQ(new_shifts.size(), 0);
  ASSERT_EQ(paused_shifts.size(), 0);
  ASSERT_EQ(closed_shifts.size(), 2);
  ASSERT_TRUE(find(closed_shifts, "c1"));
  ASSERT_TRUE(find(closed_shifts, "c2"));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c1_new;
  shifts_map_c1_new.TryAddShift(std::make_shared<WmsShift>(WmsShift{
      cid1, "s1", depot_id, now, optional_timepoint(), ShiftStatus::kClosed}));

  grocery_checkins::models::wms::ShiftsMap shifts_map_c2_new;
  shifts_map_c2_new.TryAddShift(std::make_shared<WmsShift>(WmsShift{
      cid2, "s2", depot_id, now, optional_timepoint(), ShiftStatus::kClosed}));

  CouriersShiftsIndex old_shifts_index_updated = {
      {cid1, shifts_map_c1_new},
      {cid2, shifts_map_c2_new},
      {cid3, shifts_map_c3},
  };

  // Test closed -> in_progress
  new_shifts.clear();
  fetched_shifts[0] = WmsShift{cid1,
                               "s1",
                               depot_id,
                               now,
                               optional_timepoint(),
                               ShiftStatus::kInProgress};

  FindUpdatedShifts(fetched_shifts, old_shifts_index_updated,
                    collect(new_shifts), collect(closed_shifts),
                    collect(paused_shifts), dummy);
  ASSERT_EQ(new_shifts.size(), 1);
  ASSERT_EQ(paused_shifts.size(), 0);
  ASSERT_EQ(closed_shifts.size(), 0);
  ASSERT_TRUE(find(new_shifts, "c1"));
}

UTEST(EventNotificatorTestSuite, OpenBeforeClose) {
  auto now = ::utils::datetime::Now();

  // Fill the shifts from start
  CourierId cid1{"c1"};

  std::vector<WmsShift> fetched_shifts = {WmsShift{cid1, "s2", depot_id, now,
                                                   optional_timepoint(),
                                                   ShiftStatus::kInProgress}};

  // Prepare internal structures
  std::vector<WmsShift> new_shifts;
  std::vector<WmsShift> paused_shifts;
  std::vector<WmsShift> closed_shifts;

  grocery_checkins::models::wms::ShiftsMap shifts_map_c1;
  shifts_map_c1.TryAddShift(std::make_shared<WmsShift>(
      WmsShift{cid1, "s1", depot_id, now, optional_timepoint(),
               ShiftStatus::kInProgress}));

  CouriersShiftsIndex old_shifts_index = {{cid1, shifts_map_c1}};

  FindUpdatedShifts(fetched_shifts, old_shifts_index, collect(new_shifts),
                    collect(closed_shifts), collect(paused_shifts), dummy);
  ASSERT_EQ(closed_shifts.size(), 1);
  ASSERT_TRUE(find(closed_shifts, "c1"));
}
