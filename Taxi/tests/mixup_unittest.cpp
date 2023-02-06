#include <gtest/gtest.h>

#include <statistics/mixup.hpp>
#include <userver/utils/datetime.hpp>

namespace statistics {

const auto kNow = utils::datetime::Now();

auto Time(unsigned shift) { return kNow + std::chrono::seconds(shift); }

std::ostream& operator<<(std::ostream& os, const Event& e) {
  os << "Timestamp: "
     << std::chrono::duration_cast<std::chrono::seconds>(e.timestamp - kNow)
            .count()
     << ", count: " << e.count;
  return os;
}

bool operator==(const Event& lhs, const Event& rhs) {
  return lhs.timestamp == rhs.timestamp && lhs.count == rhs.count;
}

TEST(mixup, simple) {
  std::string service("service");
  std::string metric("metric");

  Statistics old_stats;
  old_stats[service].Append(Time(0), {{metric, 1}});
  old_stats[service].Append(Time(1), {{metric, 1}});
  Statistics new_stats;
  new_stats[service].Append(Time(2), {{metric, 1}});
  MixupStatistics(old_stats, new_stats);
  ASSERT_TRUE(old_stats[service].HasEvents());
  ASSERT_EQ(old_stats[service][metric][0], (Event{Time(0), 1}));
  ASSERT_EQ(old_stats[service][metric][1], (Event{Time(1), 1}));
  ASSERT_EQ(old_stats[service][metric][2], (Event{Time(2), 1}));
  ASSERT_EQ(old_stats[service][metric].Count(), 3);
}

TEST(mixup, inserts) {
  std::string service("service");
  std::string metric("metric");

  Statistics old_stats;
  old_stats[service].Append(Time(0), {{metric, 1}});
  old_stats[service].Append(Time(1), {{metric, 1}});
  old_stats[service].Append(Time(2), {{metric, 1}});
  old_stats[service].Append(Time(4), {{metric, 1}});
  old_stats[service].Append(Time(5), {{metric, 3}});
  old_stats[service].Append(Time(6), {{metric, 1}});
  Statistics new_stats;
  new_stats[service].Append(Time(3), {{metric, 2}});
  new_stats[service].Append(Time(4), {{metric, 2}});
  new_stats[service].Append(Time(5), {{metric, 1}});
  MixupStatistics(old_stats, new_stats);
  ASSERT_TRUE(old_stats[service].HasEvents());
  ASSERT_EQ(old_stats[service][metric][0], (Event{Time(0), 1}));
  ASSERT_EQ(old_stats[service][metric][1], (Event{Time(1), 1}));
  ASSERT_EQ(old_stats[service][metric][2], (Event{Time(2), 1}));
  ASSERT_EQ(old_stats[service][metric][3], (Event{Time(3), 2}));
  // old value shall be overwritten by new one from DB
  ASSERT_EQ(old_stats[service][metric][4], (Event{Time(4), 2}));
  ASSERT_EQ(old_stats[service][metric][5], (Event{Time(5), 1}));
  ASSERT_EQ(old_stats[service][metric][6], (Event{Time(6), 1}));
  ASSERT_EQ(old_stats[service][metric].Count(), 9);
}

}  // namespace statistics
