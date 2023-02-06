#include <random>

#include <types/range.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

using namespace rules_match::types;
namespace {
const auto kEmptyJson = formats::json::FromString("{}");

const auto kWithoutKeyJsonInt = formats::json::FromString("{\"begin\": 1}");
const auto kEmptyWithNullJsonIntRange =
    formats::json::FromString("{\"begin\": 1, \"end\": null}");
const auto kJsonIntRange =
    formats::json::FromString("{\"begin\": 3, \"end\": 4}");

const auto kWithoutKeyJsonDouble =
    formats::json::FromString("{\"begin\": 1.0}");
const auto kEmptyWithNullJsonDoubleRange =
    formats::json::FromString("{\"begin\": 1.0, \"end\": null}");
const auto kJsonDoubleRange =
    formats::json::FromString("{\"begin\": 3.0, \"end\": 4.0}");

TimeRange MakeTimeRange(std::chrono::system_clock::time_point now,
                        bool is_start_utc, bool is_end_utc) {
  std::random_device rd;
  std::mt19937 gen{rd()};
  std::uniform_int_distribution<> distrib{1, 100};

  const auto begin = now + TimePoint::Duration{distrib(gen)};
  const auto end = begin + TimePoint::Duration{distrib(gen)};
  return TimeRange{TimePoint{begin, is_start_utc}, TimePoint{end, is_end_utc}};
}

}  // namespace

TEST(TimeRange, OrderingUTC) {
  const auto now = utils::datetime::Now();

  const auto time_range_utc = MakeTimeRange(now, true, true);
  const auto time_range_begin_utc = MakeTimeRange(now, true, false);
  const auto time_range_end_utc = MakeTimeRange(now, false, true);
  const auto time_range = MakeTimeRange(now, false, false);

  EXPECT_LT(time_range_utc, time_range_begin_utc);
  EXPECT_LT(time_range_utc, time_range_end_utc);
  EXPECT_LT(time_range_utc, time_range);

  EXPECT_LT(time_range_begin_utc, time_range_end_utc);
  EXPECT_LT(time_range_begin_utc, time_range);

  EXPECT_LT(time_range_end_utc, time_range);
}

class TimeRangeFixture : public testing::TestWithParam<std::tuple<bool, bool>> {
};

TEST_P(TimeRangeFixture, Ordering) {
  const auto& param = GetParam();
  const auto is_start_utc = std::get<0>(param);
  const auto is_end_utc = std::get<1>(param);

  const auto t0 = utils::datetime::Now();
  const auto t1 = t0 + TimePoint::Duration{1};
  const auto t2 = t1 + TimePoint::Duration{1};
  const auto t3 = t2 + TimePoint::Duration{1};
  const auto t4 = t3 + TimePoint::Duration{1};
  const TimeRange time_range{TimePoint{t1, is_start_utc},
                             TimePoint{t3, is_end_utc}};

  EXPECT_LT((TimeRange{TimePoint{t0, is_start_utc}, TimePoint{t1, is_end_utc}}),
            time_range);

  const TimeRange t0_t2{TimePoint{t0, is_start_utc}, TimePoint{t2, is_end_utc}};
  EXPECT_FALSE(time_range < t0_t2 || t0_t2 < time_range);

  const TimeRange t0_t3{TimePoint{t0, is_start_utc}, TimePoint{t3, is_end_utc}};
  EXPECT_FALSE(time_range < t0_t3 || t0_t3 < time_range);

  const TimeRange t0_t4{TimePoint{t0, is_start_utc}, TimePoint{t4, is_end_utc}};
  EXPECT_FALSE(time_range < t0_t4 || t0_t4 < time_range);

  const TimeRange t1_t2{TimePoint{t1, is_start_utc}, TimePoint{t2, is_end_utc}};
  EXPECT_FALSE(time_range < t1_t2 || t1_t2 < time_range);

  const TimeRange t1_t3{TimePoint{t1, is_start_utc}, TimePoint{t3, is_end_utc}};
  EXPECT_FALSE(time_range < t1_t3 || t1_t3 < time_range);

  const TimeRange t1_t4{TimePoint{t1, is_start_utc}, TimePoint{t4, is_end_utc}};
  EXPECT_FALSE(time_range < t1_t4 || t1_t4 < time_range);

  const TimeRange t2_t3{TimePoint{t2, is_start_utc}, TimePoint{t3, is_end_utc}};
  EXPECT_FALSE(time_range < t2_t3 || t2_t3 < time_range);

  const TimeRange t2_t4{TimePoint{t2, is_start_utc}, TimePoint{t4, is_end_utc}};
  EXPECT_FALSE(time_range < t2_t4 || t2_t4 < time_range);

  EXPECT_LT(time_range, (TimeRange{TimePoint{t3, is_start_utc},
                                   TimePoint{t4, is_end_utc}}));

  const TimeRange t0_t0{TimePoint{t0, is_start_utc}, TimePoint{t0, is_end_utc}};
  const TimeRange t1_t1{TimePoint{t1, is_start_utc}, TimePoint{t1, is_end_utc}};
  const TimeRange t2_t2{TimePoint{t2, is_start_utc}, TimePoint{t2, is_end_utc}};

  EXPECT_LT(t0_t0, time_range);
  EXPECT_LT(t1_t1, time_range);
  EXPECT_LT(t2_t2, time_range);
  EXPECT_LT(time_range, (TimeRange{TimePoint{t3, is_start_utc},
                                   TimePoint{t3, is_end_utc}}));
  EXPECT_LT(time_range, (TimeRange{TimePoint{t4, is_start_utc},
                                   TimePoint{t4, is_end_utc}}));

  EXPECT_LT(t0_t0, t1_t1);
  EXPECT_EQ(t1_t1, t1_t1);
  EXPECT_LT(t1_t1, t2_t2);
}

TEST_P(TimeRangeFixture, IsEmpty) {
  const auto& param = GetParam();
  const auto begin = utils::datetime::Now();
  const auto end = begin;
  const auto is_start_utc = std::get<0>(param);
  const auto is_end_utc = std::get<1>(param);

  EXPECT_NO_THROW(
      (TimeRange{TimePoint{begin, is_start_utc}, TimePoint{end, is_end_utc}}));
  EXPECT_TRUE(
      (TimeRange{TimePoint{begin, is_start_utc}, TimePoint{end, is_end_utc}}
           .IsEmpty()));
  EXPECT_FALSE(MakeTimeRange(begin, is_start_utc, is_end_utc).IsEmpty());
}

TEST_P(TimeRangeFixture, TimeRange) {
  const auto& param = GetParam();
  const auto end = utils::datetime::Now();
  const auto begin = end + TimePoint::Duration{300};

  EXPECT_THROW((TimeRange{TimePoint{begin, std::get<0>(param)},
                          TimePoint{end, std::get<1>(param)}}),
               rules_match::ValidationError);
}

TEST_P(TimeRangeFixture, UpdateFails) {
  const auto& param = GetParam();
  const auto now = utils::datetime::Now();
  auto time_range = MakeTimeRange(now, std::get<0>(param), std::get<1>(param));

  const auto begin = time_range.GetBegin().time;
  const auto end = time_range.GetEnd().time;
  EXPECT_THROW(
      time_range.Update(TimePoint{end, false}, TimePoint{begin, false}),
      rules_match::ValidationError);
  EXPECT_THROW(time_range.Update(TimePoint{end, false}, TimePoint{begin, true}),
               rules_match::ValidationError);
  EXPECT_THROW(time_range.Update(TimePoint{end, true}, TimePoint{begin, false}),
               rules_match::ValidationError);
  EXPECT_THROW(time_range.Update(TimePoint{end, true}, TimePoint{begin, true}),
               rules_match::ValidationError);

  EXPECT_THROW(time_range.Update(std::nullopt, TimePoint{begin, false}),
               rules_match::ValidationError);
  EXPECT_THROW(time_range.Update(std::nullopt, TimePoint{begin, true}),
               rules_match::ValidationError);

  EXPECT_THROW(time_range.Update(TimePoint{end, false}, std::nullopt),
               rules_match::ValidationError);
  EXPECT_THROW(time_range.Update(TimePoint{end, true}, std::nullopt),
               rules_match::ValidationError);
}

TEST_P(TimeRangeFixture, UpdateSuccess) {
  const auto& param = GetParam();
  const auto now = utils::datetime::Now();
  auto time_range = MakeTimeRange(now, std::get<0>(param), std::get<1>(param));

  auto new_time_range = MakeTimeRange(time_range.GetEnd().time, false, false);
  time_range.Update(new_time_range.GetBegin(), new_time_range.GetEnd());
  EXPECT_EQ(time_range, new_time_range);

  new_time_range = MakeTimeRange(time_range.GetEnd().time, false, true);
  time_range.Update(new_time_range.GetBegin(), new_time_range.GetEnd());
  EXPECT_EQ(time_range, new_time_range);

  new_time_range = MakeTimeRange(time_range.GetEnd().time, true, false);
  time_range.Update(new_time_range.GetBegin(), new_time_range.GetEnd());
  EXPECT_EQ(time_range, new_time_range);

  new_time_range = MakeTimeRange(time_range.GetEnd().time, true, true);
  time_range.Update(new_time_range.GetBegin(), new_time_range.GetEnd());
  EXPECT_EQ(time_range, new_time_range);

  new_time_range = MakeTimeRange(time_range.GetEnd().time, false, false);
  auto begin = time_range.GetBegin();
  time_range.Update(std::nullopt, new_time_range.GetEnd());
  EXPECT_EQ(time_range, (TimeRange{begin, new_time_range.GetEnd()}));

  new_time_range = MakeTimeRange(time_range.GetEnd().time, false, true);
  begin = time_range.GetBegin();
  time_range.Update(std::nullopt, new_time_range.GetEnd());
  EXPECT_EQ(time_range, (TimeRange{begin, new_time_range.GetEnd()}));

  new_time_range = MakeTimeRange(time_range.GetEnd().time, false, false);
  std::swap(time_range, new_time_range);
  auto end = time_range.GetEnd();
  time_range.Update(new_time_range.GetBegin(), std::nullopt);
  EXPECT_EQ(time_range, (TimeRange{new_time_range.GetBegin(), end}));

  new_time_range = MakeTimeRange(time_range.GetEnd().time, true, false);
  std::swap(time_range, new_time_range);
  end = time_range.GetEnd();
  time_range.Update(new_time_range.GetBegin(), std::nullopt);
  EXPECT_EQ(time_range, (TimeRange{new_time_range.GetBegin(), end}));
}

TEST_P(TimeRangeFixture, Equal) {
  const auto& param = GetParam();
  const auto now = utils::datetime::Now();
  const auto time_range =
      MakeTimeRange(now, std::get<0>(param), std::get<1>(param));

  const auto begin = time_range.GetBegin();
  const auto end = time_range.GetEnd();

  EXPECT_EQ(time_range, time_range);
  EXPECT_EQ(time_range, (TimeRange{begin, end}));

  EXPECT_NE(time_range, (TimeRange{TimePoint{begin.time, !begin.is_utc}, end}));
  EXPECT_NE(time_range, (TimeRange{begin, TimePoint{end.time, !end.is_utc}}));
  EXPECT_NE(time_range, (TimeRange{TimePoint{begin.time, !begin.is_utc},
                                   TimePoint{end.time, !end.is_utc}}));
  EXPECT_NE(time_range, MakeTimeRange(end.time, begin.is_utc, end.is_utc));
}

INSTANTIATE_TEST_SUITE_P(TimeRange, TimeRangeFixture,
                         testing::Combine(testing::Bool(), testing::Bool()));

TEST(Range, InvalidConstructor) {
  EXPECT_THROW((IntRange{1, -4}), rules_match::ValidationError);
  EXPECT_THROW((IntRange{1, 1}), rules_match::ValidationError);

  EXPECT_THROW((DoubleRange{1., -4.}), rules_match::ValidationError);
  EXPECT_THROW((DoubleRange{1., 1.}), rules_match::ValidationError);
}

TEST(Range, Equal) {
  EXPECT_EQ((IntRange{1, 2}), (IntRange{1, 2}));
  EXPECT_EQ((IntRange{1, {}}), (IntRange{1, {}}));

  EXPECT_EQ((DoubleRange{1., 2.}), (DoubleRange{1., 2.}));
  EXPECT_EQ((DoubleRange{1, {}}), (DoubleRange{1., {}}));
}

TEST(Range, Compare) {
  EXPECT_FALSE((IntRange{1, 2}) < (IntRange{1, 2}));
  EXPECT_TRUE((IntRange{1, 2}) < (IntRange{1, {}}));
  EXPECT_FALSE((IntRange{1, {}}) < (IntRange{1, 2}));
  EXPECT_FALSE((IntRange{1, {}}) < (IntRange{1, {}}));
  EXPECT_TRUE((IntRange{1, 2}) < (IntRange{2, 3}));
  EXPECT_FALSE((IntRange{2, 3}) < (IntRange{1, 4}));

  EXPECT_FALSE((DoubleRange{1., 2.}) < (DoubleRange{1., 2.}));
  EXPECT_TRUE((DoubleRange{1., 2.}) < (DoubleRange{1., {}}));
  EXPECT_FALSE((DoubleRange{1., {}}) < (DoubleRange{1., 2.}));
  EXPECT_FALSE((DoubleRange{1., {}}) < (DoubleRange{1., {}}));
  EXPECT_TRUE((DoubleRange{1., 2.}) < (DoubleRange{2., 3.}));
  EXPECT_FALSE((DoubleRange{2., 3.}) < (DoubleRange{1., 4.}));
}

TEST(Range, Parse) {
  EXPECT_EQ(kJsonIntRange.As<IntRange>(), (IntRange{3, 4}));
  EXPECT_EQ(kEmptyWithNullJsonIntRange.As<IntRange>(), (IntRange{1, {}}));
  EXPECT_EQ(kWithoutKeyJsonInt.As<IntRange>(), (IntRange{1, {}}));
  EXPECT_THROW(kEmptyJson.As<IntRange>(), formats::json::Exception);
  EXPECT_EQ(kJsonDoubleRange.As<IntRange>(), (IntRange{3, 4}));

  EXPECT_EQ(kJsonDoubleRange.As<DoubleRange>(), (DoubleRange{3., 4.}));
  EXPECT_EQ(kEmptyWithNullJsonDoubleRange.As<DoubleRange>(),
            (DoubleRange{1., {}}));
  EXPECT_EQ(kWithoutKeyJsonDouble.As<DoubleRange>(), (DoubleRange{1., {}}));
  EXPECT_THROW(kEmptyJson.As<DoubleRange>(), formats::json::Exception);
  EXPECT_EQ(kJsonIntRange.As<DoubleRange>(), (DoubleRange{3., 4.}));
}

TEST(Range, Serialize) {
  EXPECT_EQ(formats::json::ValueBuilder((IntRange{3, 4})).ExtractValue(),
            kJsonIntRange);
  EXPECT_EQ(formats::json::ValueBuilder(IntRange{1, {}}).ExtractValue(),
            kEmptyWithNullJsonIntRange);

  EXPECT_EQ(formats::json::ValueBuilder(DoubleRange{3., 4.}).ExtractValue(),
            kJsonDoubleRange);
  EXPECT_EQ(formats::json::ValueBuilder(DoubleRange{1., {}}).ExtractValue(),
            kEmptyWithNullJsonDoubleRange);
}
