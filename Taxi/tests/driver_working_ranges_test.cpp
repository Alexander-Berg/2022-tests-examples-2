#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include <models/driver_working_ranges.hpp>

namespace {
using namespace models;
using namespace utils::datetime;

const auto time_00s = Stringtime("2019-01-21T15:29:00+0000");
const auto time_05s = Stringtime("2019-01-21T15:29:05+0000");
const auto time_10s = Stringtime("2019-01-21T15:29:10+0000");
const auto time_15s = Stringtime("2019-01-21T15:29:15+0000");
const auto time_20s = Stringtime("2019-01-21T15:29:20+0000");
const auto time_25s = Stringtime("2019-01-21T15:29:25+0000");
const auto time_30s = Stringtime("2019-01-21T15:29:30+0000");
const auto time_35s = Stringtime("2019-01-21T15:29:35+0000");
const auto time_40s = Stringtime("2019-01-21T15:29:40+0000");
const auto time_45s = Stringtime("2019-01-21T15:29:45+0000");
const auto time_50s = Stringtime("2019-01-21T15:29:50+0000");
const auto time_52s = Stringtime("2019-01-21T15:29:52+0000");
const auto time_55s = Stringtime("2019-01-21T15:29:55+0000");
const auto time_56s = Stringtime("2019-01-21T15:29:56+0000");

}  // namespace

TEST(DriverWorkingRanges, TimeRange) {
  {
    TimeRange first{time_00s, time_10s};
    EXPECT_EQ(first.Length(), std::chrono::seconds(10));
    EXPECT_EQ(first.ToString(),
              "[2019-01-21T15:29:00+0000, 2019-01-21T15:29:10+0000]");

    TimeRange second{time_00s, time_10s};

    EXPECT_TRUE(first == second);
    EXPECT_FALSE(TimeRanges::CmpBegin()(first, second));
  }
  {
    TimeRange first{time_00s, time_10s};
    TimeRange second{time_05s, time_10s};

    EXPECT_EQ(first.Length(), std::chrono::seconds(10));
    EXPECT_EQ(second.Length(), std::chrono::seconds(5));

    EXPECT_FALSE(first == second);
    EXPECT_TRUE(TimeRanges::CmpBegin()(first, second));
  }
}

TEST(DriverWorkingRanges, TimeRanges) {
  TimeRange first{time_00s, time_10s};
  TimeRange second{time_05s, time_10s};

  TimeRanges ranges;
  EXPECT_TRUE(ranges.Append(first));
  EXPECT_FALSE(ranges.Append(first));

  EXPECT_THROW(ranges.Append(second), TimeRanges::TimeRangesIntersectException);
}

TEST(DriverWorkingRanges, TimeRangesIntersection) {
  TimeRange first{time_10s, time_20s};
  TimeRange second{time_30s, time_40s};

  TimeRanges sample;
  EXPECT_EQ(sample.GetLastWorkingTime(), std::nullopt);
  EXPECT_TRUE(sample.Append(first));
  EXPECT_TRUE(sample.Append(second));
  EXPECT_EQ(sample.GetLastWorkingTime(), second.end);

  {
    TimeRanges ranges{sample};
    EXPECT_FALSE(ranges.Append(first));
    EXPECT_FALSE(ranges.Append(second));
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());

    EXPECT_FALSE(ranges.Append(second));
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());

    EXPECT_THROW(ranges.Append(TimeRange{time_00s, time_15s}),
                 TimeRanges::TimeRangesIntersectException);
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());

    EXPECT_THROW(ranges.Append(TimeRange{time_15s, time_25s}),
                 TimeRanges::TimeRangesIntersectException);
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());

    EXPECT_THROW(ranges.Append(TimeRange{time_25s, time_35s}),
                 TimeRanges::TimeRangesIntersectException);
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());

    EXPECT_THROW(ranges.Append(TimeRange{time_15s, time_35s}),
                 TimeRanges::TimeRangesIntersectException);
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());

    EXPECT_THROW(ranges.Append(TimeRange{time_25s, time_40s}),
                 TimeRanges::TimeRangesIntersectException);
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());
  }
  {
    TimeRanges ranges{sample};
    EXPECT_TRUE(ranges.Append(TimeRange{time_00s, time_05s}));
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());
  }
  {
    TimeRanges ranges{sample};
    EXPECT_TRUE(ranges.Append(TimeRange{time_00s, time_10s}));
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());
  }
  {
    TimeRanges ranges{sample};
    EXPECT_TRUE(ranges.Append(TimeRange{time_25s, time_30s}));
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());
  }
  {
    TimeRanges ranges{sample};
    EXPECT_TRUE(ranges.Append(TimeRange{time_20s, time_30s}));
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());
  }
  {
    TimeRanges ranges{sample};
    const auto& data = ranges.GetRanges();

    EXPECT_FALSE(ranges.Append(first));
    EXPECT_TRUE(ranges.Append(TimeRange{time_50s, time_55s}));
    EXPECT_TRUE(ranges.Append(TimeRange{time_40s, time_45s}));

    EXPECT_EQ(ranges.GetLastWorkingTime(), time_55s);

    ranges.RemoveExpired(time_05s);

    EXPECT_EQ(data.size(), 4u);
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());

    // [10,20] [30,40] [40,45] [50,55]
    {
      auto copy = ranges;
      copy.RemoveExpired(time_05s);
      EXPECT_EQ(copy.GetRanges().size(), 4u);
      copy.RemoveExpired(time_10s);
      EXPECT_EQ(copy.GetRanges().size(), 4u);
      copy.RemoveExpired(time_15s);
      EXPECT_EQ(copy.GetRanges().size(), 4u);
    }
    {
      auto copy = ranges;
      copy.RemoveExpired(time_20s);
      EXPECT_EQ(copy.GetRanges().size(), 3u);
    }
    {
      auto copy = ranges;
      copy.RemoveExpired(time_25s);
      EXPECT_EQ(copy.GetRanges().size(), 3u);
    }
    {
      auto copy = ranges;
      copy.RemoveExpired(time_30s);
      EXPECT_EQ(copy.GetRanges().size(), 3u);
    }
    {
      auto copy = ranges;
      copy.RemoveExpired(time_35s);
      EXPECT_EQ(copy.GetRanges().size(), 3u);
    }

    ranges.RemoveExpired(time_35s);
    EXPECT_EQ(data.size(), 3u);
    EXPECT_EQ(*data.begin(), second);
    EXPECT_EQ(*data.rbegin(), (TimeRange{time_50s, time_55s}));

    ranges.RemoveExpired(time_35s);  // nothing changed
    EXPECT_EQ(data.size(), 3u);
    ranges.RemoveExpired(time_40s);
    EXPECT_EQ(data.size(), 2u);
    ranges.RemoveExpired(time_50s);
    EXPECT_EQ(data.size(), 1u);
    ranges.RemoveExpired(time_52s);
    EXPECT_EQ(data.size(), 1u);
    ranges.RemoveExpired(time_56s);
    EXPECT_TRUE(ranges.Empty());
    ranges.RemoveExpired(time_05s);
  }
}

TEST(DriverWorkingRanges, TimeRangesUpdate) {
  TimeRange first{time_10s, time_20s};
  TimeRange second{time_30s, time_40s};

  TimeRanges sample;
  EXPECT_TRUE(sample.Append(first));
  EXPECT_TRUE(sample.Append(second));

  {
    TimeRanges ranges{sample};

    TimeRange append{time_15s, time_20s};
    EXPECT_THROW(ranges.Append(append),
                 TimeRanges::TimeRangesIntersectException);
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());

    EXPECT_TRUE(ranges.Append(TimeRange{time_10s, time_15s}));
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());

    EXPECT_TRUE(ranges.Append(append));

    EXPECT_TRUE(ranges.Append(TimeRange{time_30s, time_35s}));
  }
  {
    TimeRanges ranges{sample};
    EXPECT_TRUE(ranges.Append(TimeRange{time_10s, time_25s}));
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());
  }
  {
    TimeRanges ranges{sample};
    EXPECT_TRUE(ranges.Append(TimeRange{time_10s, time_30s}));
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());
  }
  {
    TimeRanges ranges{sample};
    EXPECT_TRUE(ranges.Append(TimeRange{time_30s, time_55s}));
    EXPECT_NE(ranges.GetRanges(), sample.GetRanges());
  }
  {
    TimeRanges ranges{sample};
    EXPECT_TRUE(ranges.Append(TimeRange{time_10s, time_25s}));
    EXPECT_TRUE(ranges.Append(TimeRange{time_30s, time_55s}));
    const auto& data = ranges.GetRanges();
    EXPECT_EQ(data.size(), 2u);
    EXPECT_EQ(*data.begin(), (TimeRange{time_10s, time_25s}));
    EXPECT_EQ(*data.rbegin(), (TimeRange{time_30s, time_55s}));
  }
  {
    TimeRanges ranges{sample};

    EXPECT_THROW(ranges.Append(TimeRange{time_10s, time_35s}),
                 TimeRanges::TimeRangesIntersectException);
    EXPECT_EQ(ranges.GetRanges(), sample.GetRanges());
  }
}
