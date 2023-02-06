#include <gtest/gtest.h>
#include <utils/match.hpp>

namespace grocery_performer_mentorship {

using namespace std::chrono_literals;
using grocery_performer_mentorship::utils::Match;
using grocery_performer_mentorship::utils::ShiftPlus;
using grocery_shared::DepotId;
using grocery_shared::LegacyDepotId;

TEST(MatchAlgo, MatchSimplePositive) {
  auto starts = std::chrono::system_clock::now() + 1h;
  auto ends = starts + 4h;
  models::Shift mentor = {"123_001",
                          "1002",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          starts,
                          ends,
                          models::Shift::Status::kWaiting};
  models::Shift newbie = {"123_101",
                          "1001",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          starts,
                          ends,
                          models::Shift::Status::kWaiting};
  auto pairs = Match({newbie}, {{mentor, 0}}, 2h);
  ASSERT_EQ(pairs.size(), 1);
  ASSERT_TRUE(pairs[0].mentor);
  ASSERT_EQ(pairs[0].newbie.depot_id, DepotId{"FFFF123"});
  ASSERT_EQ(pairs[0].newbie.shift_id, "1001");
  ASSERT_EQ(pairs[0].mentor->shift_id, "1002");
  ASSERT_EQ(pairs[0].mentor->depot_id, DepotId{"FFFF123"});
}

TEST(MatchAlgo, MatchWithTheLowestCounter) {
  auto starts = std::chrono::system_clock::now() + 1h;
  auto ends = starts + 4h;
  models::Shift mentor = {"123_001",
                          "1002",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          starts,
                          ends,
                          models::Shift::Status::kWaiting};
  models::Shift mentor2 = {"123_001",
                           "1002",
                           DepotId{"FFFF123"},
                           LegacyDepotId{"123"},
                           starts,
                           ends,
                           models::Shift::Status::kWaiting};
  models::Shift newbie = {"123_101",
                          "1001",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          starts,
                          ends,
                          models::Shift::Status::kWaiting};
  auto pairs = Match({newbie}, {{mentor, 5}, {mentor2, 2}}, 2h);
  ASSERT_EQ(pairs.size(), 1);
  ASSERT_TRUE(pairs[0].mentor);
  ASSERT_EQ(pairs[0].newbie.depot_id, DepotId{"FFFF123"});
  ASSERT_EQ(pairs[0].newbie.shift_id, "1001");
  ASSERT_EQ(pairs[0].mentor->shift_id, "1002");
  ASSERT_EQ(pairs[0].mentor->depot_id, DepotId{"FFFF123"});
}

TEST(MatchAlgo, MatchSimpleNegativeNoMinOverlap) {
  auto starts = std::chrono::system_clock::now() + 1h;
  auto ends = starts + 4h;
  models::Shift mentor = {"123_001",
                          "1002",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          starts,
                          ends,
                          models::Shift::Status::kWaiting};
  models::Shift newbie = {"123_101",
                          "1001",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          starts + 3h,
                          ends + 3h,
                          models::Shift::Status::kWaiting};
  auto pairs = Match({newbie}, {{mentor, 0}}, 2h);
  ASSERT_EQ(pairs.size(), 1);
  ASSERT_EQ(pairs[0].newbie.depot_id, DepotId{"FFFF123"});
  ASSERT_EQ(pairs[0].newbie.shift_id, "1001");
  ASSERT_FALSE(pairs[0].mentor);
}

TEST(MatchAlgo, MatchSimpleNegativeSecondHour) {
  auto now = std::chrono::system_clock::now() + 1h;
  models::Shift mentor = {"123_001",
                          "1002",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          now + 1h,
                          now + 4h,
                          models::Shift::Status::kWaiting};
  models::Shift newbie = {"123_101",
                          "1001",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          now,
                          now + 4h,
                          models::Shift::Status::kWaiting};
  auto pairs = Match({newbie}, {{mentor, 0}}, 2h);
  ASSERT_EQ(pairs.size(), 1);
  ASSERT_EQ(pairs[0].newbie.depot_id, DepotId{"FFFF123"});
  ASSERT_EQ(pairs[0].newbie.shift_id, "1001");
  ASSERT_FALSE(pairs[0].mentor);
}

TEST(MatchAlgo, MatchSimpleNegativeDifferentDepots) {
  auto starts = std::chrono::system_clock::now() + 1h;
  auto ends = starts + 4h;
  models::Shift mentor = {"123_001",
                          "1002",
                          DepotId{"FFFF124"},
                          LegacyDepotId{"124"},
                          starts,
                          ends,
                          models::Shift::Status::kWaiting};
  models::Shift newbie = {"123_101",
                          "1001",
                          DepotId{"FFFF123"},
                          LegacyDepotId{"123"},
                          starts,
                          ends,
                          models::Shift::Status::kWaiting};
  auto pairs = Match({newbie}, {{mentor, 0}}, 2h);
  ASSERT_EQ(pairs.size(), 1);
  ASSERT_EQ(pairs[0].newbie.depot_id, DepotId{"FFFF123"});
  ASSERT_EQ(pairs[0].newbie.shift_id, "1001");
  ASSERT_FALSE(pairs[0].mentor);
}

TEST(MatchAlgo, MatchTwoCompetingNewbiesCase1) {
  auto now = std::chrono::system_clock::now();
  std::vector<ShiftPlus> mentors = {
      {{"123_001", "1001", DepotId{"FFFF123"}, LegacyDepotId{"123"}, now,
        now + 4h, models::Shift::Status::kWaiting},
       0},
      {{"123_002", "1003", DepotId{"FFFF123"}, LegacyDepotId{"123"}, now + 2h,
        now + 7h, models::Shift::Status::kWaiting},
       0}};
  models::Shifts newbies = {
      {"123_101", "1002", DepotId{"FFFF123"}, LegacyDepotId{"123"}, now + 2h,
       now + 6h, models::Shift::Status::kWaiting},
      {"123_102", "1004", DepotId{"FFFF123"}, LegacyDepotId{"123"}, now + 4h,
       now + 8h, models::Shift::Status::kWaiting}};

  //                                     //
  //          |---newbie1---|            //
  //  |--mentor1----|  |---newbie2----|  //
  //          |----mentor2---|           //
  // now ----------- time -------------> //
  auto pairs = Match(newbies, mentors, 2h);
  ASSERT_EQ(pairs.size(), 2);
  for (auto& item : pairs) {
    ASSERT_EQ(item.newbie.depot_id, DepotId{"FFFF123"});
    ASSERT_EQ(item.newbie.legacy_depot_id, LegacyDepotId{"123"});
    ASSERT_TRUE(item.mentor);
    if (item.newbie.performer_id == "123_101") {
      ASSERT_EQ(item.mentor->performer_id, "123_001");
    } else {
      ASSERT_EQ(item.newbie.performer_id, "123_102");
      ASSERT_EQ(item.mentor->performer_id, "123_002");
    }
  }
}

TEST(MatchAlgo, MatchTwoCompetingNewbiesCase2) {
  auto now = std::chrono::system_clock::now();
  std::vector<ShiftPlus> mentors = {
      {{"123_001", "1001", DepotId{"FFFF123"}, LegacyDepotId{"123"}, now,
        now + 4h, models::Shift::Status::kWaiting},
       0},
      {{"123_002", "1003", DepotId{"FFFF123"}, LegacyDepotId{"123"}, now + 3h,
        now + 6h, models::Shift::Status::kWaiting},
       0}};
  models::Shifts newbies = {
      {"123_101", "1002", DepotId{"FFFF123"}, LegacyDepotId{"123"}, now + 2h,
       now + 2h + 4h, models::Shift::Status::kWaiting},
      {"123_102", "1004", DepotId{"FFFF123"}, LegacyDepotId{"123"}, now + 5h,
       now + 8h, models::Shift::Status::kWaiting}};
  // newbie2 can't be matched                  //
  // due to it has small overlap with mentor2  //
  //                                           //
  //          |---newbie1---|                  //
  //  |--mentor1----|       |---newbie2----| //
  //          |----mentor2---|                 //
  // now ----------- time ----------------->   //
  auto pairs = Match(newbies, mentors, 2h);
  ASSERT_EQ(pairs.size(), 2);
  for (auto& item : pairs) {
    ASSERT_EQ(item.newbie.depot_id, DepotId{"FFFF123"});
    ASSERT_EQ(item.newbie.legacy_depot_id, LegacyDepotId{"123"});
    if (item.newbie.performer_id == "123_101") {
      ASSERT_TRUE(item.mentor->performer_id == "123_001" ||
                  item.mentor->performer_id == "123_002");
    } else {
      ASSERT_FALSE(pairs[0].mentor);
    }
  }
}

}  // namespace grocery_performer_mentorship
