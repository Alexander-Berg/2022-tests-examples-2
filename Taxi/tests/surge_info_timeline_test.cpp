#include <vector>

#include <boost/math/special_functions/next.hpp>

#include <gtest/gtest.h>

#include <grocery-surge-shared/models/surge_info.hpp>

namespace grocery_surge_shared::models {

}  // namespace grocery_surge_shared::models

namespace tests {

struct TestSurgeInfo {
  double load_level;
  formats::json::Value calculation_meta;
};

bool operator==(const TestSurgeInfo& lhs, const TestSurgeInfo& rhs) {
  const auto n_ulps =
      boost::math::float_distance(lhs.load_level, rhs.load_level);
  return std::abs(n_ulps) < 1;
}

struct TimePointHash {
  auto operator()(const std::chrono::system_clock::time_point& tp) const {
    return std::hash<std::size_t>{}(tp.time_since_epoch().count());
  }
};

auto MakeTimestamps(std::initializer_list<int> values) {
  std::vector<std::chrono::system_clock::time_point> res;
  res.reserve(values.size());

  for (const auto& v : values) {
    res.push_back(
        std::chrono::system_clock::time_point{std::chrono::seconds{v}});
  }

  return res;
}

auto MakeSurgeInfoPerPipeline(
    std::initializer_list<std::pair<std::string, double>> values) {
  grocery_surge_shared::models::SurgeInfoPerPipeline<TestSurgeInfo> res;
  res.reserve(values.size());

  for (const auto& [k, v] : values) {
    res[grocery_surge_shared::js::PipelineName{k}] =
        TestSurgeInfo{v, formats::json::Value{}};
  }

  return res;
}

void TestMerge(std::vector<std::chrono::system_clock::time_point> a,
               std::vector<std::chrono::system_clock::time_point> b,
               std::vector<std::chrono::system_clock::time_point> expected) {
  using Pair = std::pair<
      std::chrono::system_clock::time_point,
      grocery_surge_shared::models::SurgeInfoPerPipeline<TestSurgeInfo>>;

  std::vector<Pair> timeline_data_1, timeline_data_2;

  for (const auto& tp : a) {
    timeline_data_1.push_back(Pair{tp, {}});
  }

  for (const auto& tp : b) {
    timeline_data_2.emplace_back(Pair{tp, {}});
  }

  grocery_surge_shared::models::SurgeInfoTimeline<TestSurgeInfo> timeline1;
  grocery_surge_shared::models::SurgeInfoTimeline<TestSurgeInfo> timeline2;
  timeline1.InsertNew(timeline_data_1.begin(), timeline_data_1.end());
  timeline2.InsertNew(timeline_data_2.begin(), timeline_data_2.end());

  timeline1.Merge(timeline2);

  auto first = timeline1.LookUp(std::chrono::system_clock::time_point::max());
  auto last = timeline1.LookUp(std::chrono::system_clock::time_point::min());

  std::vector<std::chrono::system_clock::time_point> res;

  for (; first != last; ++first) {
    res.push_back(first->timestamp);
  }

  EXPECT_EQ(expected, res);
}

}  // namespace tests

TEST(SurgeInfoTimeline, LookUp) {
  grocery_surge_shared::models::SurgeInfoTimeline<tests::TestSurgeInfo>
      timeline;
  const auto timestamps = tests::MakeTimestamps({100, 110, 120, 130});
  const auto ref_surge_info =
      tests::MakeSurgeInfoPerPipeline({{"pipeline_1", 10}, {"pipeline_2", 20}});

  std::unordered_map<
      std::chrono::system_clock::time_point,
      grocery_surge_shared::models::SurgeInfoPerPipeline<tests::TestSurgeInfo>,
      tests::TimePointHash>
      timeline_data{{timestamps[0], {}},
                    {timestamps[1], ref_surge_info},
                    {timestamps[2], {}},
                    {timestamps[3], {}}};

  // Тестим константные итераторы.
  timeline.InsertNew(timeline_data.cbegin(), timeline_data.cend());

  // Запросим не точный таймстемп, должен вернуться ближайший предыдущий.
  const auto itr = timeline.LookUp(timestamps[1] + std::chrono::seconds{2});

  ASSERT_NE(timeline.End(), itr);
  EXPECT_EQ(timestamps[1], itr->timestamp);
  EXPECT_EQ(ref_surge_info, itr->surge_info);
}

// Хотим получить значение, которое раньше первого известного суржа.
TEST(SurgeInfoTimeline, LookUpMissingValue) {
  grocery_surge_shared::models::SurgeInfoTimeline<tests::TestSurgeInfo>
      timeline;
  const auto timestamps = tests::MakeTimestamps({100, 110, 120, 130});

  std::unordered_map<
      std::chrono::system_clock::time_point,
      grocery_surge_shared::models::SurgeInfoPerPipeline<tests::TestSurgeInfo>,
      tests::TimePointHash>
      timeline_data{{timestamps[0], {}},
                    {timestamps[1], {}},
                    {timestamps[2], {}},
                    {timestamps[3], {}}};

  // Тестим обычные итераторы.
  timeline.InsertNew(timeline_data.begin(), timeline_data.end());

  const auto itr = timeline.LookUp(timestamps[0] - std::chrono::seconds{2});

  ASSERT_EQ(timeline.End(), itr);
}

// Хотим получить значение, которое больше последнего известного суржа.
TEST(SurgeInfoTimeline, LookUpLatestValue) {
  grocery_surge_shared::models::SurgeInfoTimeline<tests::TestSurgeInfo>
      timeline;
  const auto timestamps = tests::MakeTimestamps({100, 110, 120, 130});

  std::unordered_map<
      std::chrono::system_clock::time_point,
      grocery_surge_shared::models::SurgeInfoPerPipeline<tests::TestSurgeInfo>,
      tests::TimePointHash>
      timeline_data{{timestamps[0], {}},
                    {timestamps[1], {}},
                    {timestamps[2], {}},
                    {timestamps[3], {}}};

  timeline.InsertNew(std::move_iterator(timeline_data.begin()),
                     std::move_iterator(timeline_data.end()));

  const auto itr =
      timeline.LookUp(std::chrono::system_clock::time_point::max());

  ASSERT_NE(timeline.End(), itr);
  ASSERT_EQ(timestamps[3], itr->timestamp);
}

TEST(SurgeInfoTimeline, Clean) {
  grocery_surge_shared::models::SurgeInfoTimeline<tests::TestSurgeInfo>
      timeline;
  const auto timestamps = tests::MakeTimestamps({100, 110, 120, 130, 140});

  std::unordered_map<
      std::chrono::system_clock::time_point,
      grocery_surge_shared::models::SurgeInfoPerPipeline<tests::TestSurgeInfo>,
      tests::TimePointHash>
      timeline_data;

  for (const auto& tp : timestamps) {
    timeline_data[tp] = {};
  }

  timeline.InsertNew(timeline_data.cbegin(), timeline_data.cend());

  for (const auto& clean_tp : timestamps) {
    timeline.Clean(clean_tp);

    for (const auto& tp : timestamps) {
      const auto itr = timeline.LookUp(tp);

      if (tp < clean_tp) {
        EXPECT_EQ(timeline.End(), itr);
      } else {
        EXPECT_NE(timeline.End(), itr);
      }
    }
  }
}

TEST(SurgeInfoTimeline, InsertNewIgnoresOlderTimestamps) {
  grocery_surge_shared::models::SurgeInfoTimeline<tests::TestSurgeInfo>
      timeline;
  const auto timestamps_1 = tests::MakeTimestamps({130, 100, 110, 140, 120});
  const auto timestamps_2 =
      tests::MakeTimestamps({165, 135, 145, 155, 105, 115, 125});

  using Pair = std::pair<
      std::chrono::system_clock::time_point,
      grocery_surge_shared::models::SurgeInfoPerPipeline<tests::TestSurgeInfo>>;

  std::vector<Pair> timeline_data_1, timeline_data_2;

  for (const auto& tp : timestamps_1) {
    timeline_data_1.push_back(Pair{tp, {}});
  }

  for (const auto& tp : timestamps_2) {
    timeline_data_2.emplace_back(Pair{tp, {}});
  }

  timeline.InsertNew(timeline_data_1.begin(), timeline_data_1.end());

  ASSERT_EQ(timestamps_1.size(), timeline.GetSize());

  // Все таймстемпы кроме `145` должны быть проигнорированы.
  timeline.InsertNew(timeline_data_2.begin(), timeline_data_2.end());

  // Проверим, что инкрементальный апдейт прошел верно.
  const auto expected_timestamps =
      tests::MakeTimestamps({165, 155, 145, 140, 130, 120, 110, 100});

  auto first = timeline.LookUp(std::chrono::system_clock::time_point::max());
  auto last = timeline.LookUp(std::chrono::system_clock::time_point::min());

  std::vector<std::chrono::system_clock::time_point> res;

  for (; first != last; ++first) {
    res.push_back(first->timestamp);
  }

  EXPECT_EQ(expected_timestamps, res);
}

TEST(SurgeInfoTimeline, MergePartialIntersection) {
  tests::TestMerge(tests::MakeTimestamps({1}), tests::MakeTimestamps({1, 3}),
                   tests::MakeTimestamps({3, 1}));

  tests::TestMerge(tests::MakeTimestamps({1, 3}), tests::MakeTimestamps({1}),
                   tests::MakeTimestamps({3, 1}));

  tests::TestMerge(tests::MakeTimestamps({2, 3, 4}),
                   tests::MakeTimestamps({2, 3, 4}),
                   tests::MakeTimestamps({4, 3, 2}));

  tests::TestMerge(tests::MakeTimestamps({1, 2, 3, 4, 5}),
                   tests::MakeTimestamps({2, 3, 4}),
                   tests::MakeTimestamps({5, 4, 3, 2, 1}));

  tests::TestMerge(tests::MakeTimestamps({1, 3, 5, 6}),
                   tests::MakeTimestamps({2, 3, 4, 7}),
                   tests::MakeTimestamps({7, 6, 5, 4, 3, 2, 1}));
}

TEST(SurgeInfoTimeline, MergeFast) {
  tests::TestMerge(tests::MakeTimestamps({}), tests::MakeTimestamps({2, 3, 4}),
                   tests::MakeTimestamps({4, 3, 2}));

  tests::TestMerge(tests::MakeTimestamps({2, 3, 4}), tests::MakeTimestamps({}),
                   tests::MakeTimestamps({4, 3, 2}));

  tests::TestMerge(tests::MakeTimestamps({2, 3, 4}),
                   tests::MakeTimestamps({5, 7}),
                   tests::MakeTimestamps({7, 5, 4, 3, 2}));

  tests::TestMerge(tests::MakeTimestamps({7, 5}),
                   tests::MakeTimestamps({2, 3, 4}),
                   tests::MakeTimestamps({7, 5, 4, 3, 2}));
}

TEST(SurgeInfoTimeline, LookUpEmptyTimeline) {
  grocery_surge_shared::models::SurgeInfoTimeline<tests::TestSurgeInfo>
      timeline;

  ASSERT_EQ(timeline.End(),
            timeline.LookUp(std::chrono::system_clock::time_point::max()));
}
