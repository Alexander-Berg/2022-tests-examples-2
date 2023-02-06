#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>

#include "convert_interval.hpp"

namespace {

using namespace models;
using namespace driver_weariness::view::internal;
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
const auto time_55s = Stringtime("2019-01-21T15:29:55+0000");
const auto time_56s = Stringtime("2019-01-21T15:29:56+0000");
const auto time_60s = Stringtime("2019-01-21T15:30:00+0000");
const auto time_65s = Stringtime("2019-01-21T15:30:05+0000");
const auto time_70s = Stringtime("2019-01-21T15:30:10+0000");
const auto time_75s = Stringtime("2019-01-21T15:30:15+0000");

const auto _01s = std::chrono::seconds(1);
const auto _02s = std::chrono::seconds(2);
const auto _03s = std::chrono::seconds(3);
const auto _04s = std::chrono::seconds(4);
const auto _05s = std::chrono::seconds(5);
const auto _06s = std::chrono::seconds(6);
const auto _10s = std::chrono::seconds(10);
const auto _11s = std::chrono::seconds(11);

template <typename Container>
IntervalsSet ConvertToSeparateIntervals(const Container& data,
                                        std::chrono::seconds distance) {
  return driver_weariness::view::internal::ConvertToSeparateIntervals(
      IntervalsMultiSet{std::begin(data), std::end(data)}, distance);
}

}  // namespace

TEST(TestWorkingIntervals, CheckAppendWorkingInterval) {
  {
    // add same interval twice
    WorkingInterval first{time_00s, time_10s, _02s};
    WorkingInterval result{first};
    result.working_time *= 2;

    auto intervals_set = ConvertToSeparateIntervals(IntervalsSet{first}, _01s);
    EXPECT_EQ(intervals_set.size(), 1u);

    intervals_set =
        ConvertToSeparateIntervals(IntervalsMultiSet{first, first}, _01s);
    EXPECT_FALSE(intervals_set.empty());
    EXPECT_EQ(intervals_set.size(), 1u);
    EXPECT_EQ(*intervals_set.begin(), result);
  }
  {
    // add intersected intervals
    WorkingInterval first{time_00s, time_10s, _02s};
    WorkingInterval append{time_05s, time_15s, _03s};
    WorkingInterval result{first.interval.begin, append.interval.end,
                           first.working_time + append.working_time};

    auto intervals_set =
        ConvertToSeparateIntervals(IntervalsMultiSet{first, append}, _01s);
    EXPECT_EQ(intervals_set.size(), 1u);
    EXPECT_EQ(*intervals_set.begin(), result);
  }
  {
    // add two non-intersecting intervals and one intersects with first
    WorkingInterval first{time_00s, time_10s, _02s};
    WorkingInterval second{time_20s, time_25s, _04s};
    WorkingInterval append{time_05s, time_15s, _03s};

    WorkingInterval new_first{first.interval.begin, append.interval.end,
                              first.working_time + append.working_time};

    auto intervals_set =
        ConvertToSeparateIntervals(IntervalsMultiSet{first, second}, _01s);
    EXPECT_EQ(intervals_set.size(), 2u);

    intervals_set = ConvertToSeparateIntervals(
        IntervalsMultiSet{first, second, append}, _01s);
    EXPECT_EQ(intervals_set.size(), 2u);
    EXPECT_EQ(intervals_set, (IntervalsSet{new_first, second}));

    WorkingInterval result_join_06s{
        new_first.interval.begin, second.interval.end,
        new_first.working_time + second.working_time};

    EXPECT_EQ(ConvertToSeparateIntervals(intervals_set, _05s), intervals_set);
    intervals_set = ConvertToSeparateIntervals(intervals_set, _06s);
    EXPECT_EQ(intervals_set.size(), 1u);
    EXPECT_EQ(*intervals_set.begin(), result_join_06s);
  }
  {
    // add two non-intersecting intervals and one intersects both
    WorkingInterval first{time_00s, time_10s, _02s};
    WorkingInterval second{time_15s, time_20s, _04s};
    WorkingInterval append{time_05s, time_15s, _03s};

    WorkingInterval result{
        first.interval.begin, second.interval.end,
        first.working_time + second.working_time + append.working_time};

    auto intervals_set =
        ConvertToSeparateIntervals(IntervalsMultiSet{first, second}, _01s);
    EXPECT_EQ(intervals_set.size(), 2u);

    intervals_set = ConvertToSeparateIntervals(
        IntervalsMultiSet{first, second, append}, _01s);
    EXPECT_EQ(intervals_set.size(), 1u);
    EXPECT_EQ(*intervals_set.begin(), result);
  }
  {
    // add two non-intersecting intervals and one includes both
    WorkingInterval first{time_05s, time_10s, _02s};
    WorkingInterval second{time_15s, time_20s, _04s};
    WorkingInterval append{time_00s, time_25s, _02s};

    WorkingInterval result{
        append.interval.begin, append.interval.end,
        first.working_time + second.working_time + append.working_time};

    auto intervals_set =
        ConvertToSeparateIntervals(IntervalsSet{first, second}, _02s);
    EXPECT_EQ(intervals_set.size(), 2u);

    intervals_set =
        ConvertToSeparateIntervals(IntervalsSet{first, second, append}, _02s);
    EXPECT_EQ(intervals_set.size(), 1u);
    EXPECT_EQ(*intervals_set.begin(), result);
  }
}

TEST(TestWorkingIntervals, CheckAppendAndJoin) {
  WorkingInterval first{time_05s, time_15s, _02s};
  WorkingInterval second{time_25s, time_35s, _01s};
  WorkingInterval third{time_45s, time_55s, _03s};
  WorkingInterval fourth{time_65s, time_75s, _01s};

  IntervalsSet intervals_set{fourth, first, third, second};

  {
    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _10s), intervals_set);
    // join all
    WorkingInterval result{first.interval.begin, fourth.interval.end,
                           first.working_time + second.working_time +
                               third.working_time + fourth.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _11s);
    EXPECT_EQ(intervals4join.size(), 1u);
    EXPECT_EQ(*intervals4join.begin(), result);
  }
  // work with first
  {
    // appending interval intersects with first (begin)
    WorkingInterval append{first.interval.begin - _05s,
                           first.interval.end - _05s, _02s};
    WorkingInterval new_first{append.interval.begin, first.interval.end,
                              append.working_time + first.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, second, third, fourth}));

    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _10s), intervals4join);
    // join all
    WorkingInterval result{new_first.interval.begin, fourth.interval.end,
                           new_first.working_time + second.working_time +
                               third.working_time + fourth.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _11s);
    EXPECT_EQ(intervals4join.size(), 1u);
    EXPECT_EQ(*intervals4join.begin(), result);
  }
  {
    // appending interval intersects with first (end)
    WorkingInterval append{first.interval.begin + _05s,
                           first.interval.end + _05s, _01s};
    WorkingInterval new_first{first.interval.begin, append.interval.end,
                              first.working_time + append.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, second, third, fourth}));

    // add interval inside new_first
    WorkingInterval inside{new_first.interval.begin + _05s,
                           new_first.interval.end - _05s, _01s};
    intervals4join.insert(inside);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    new_first.working_time += inside.working_time;
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, second, third, fourth}));

    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _05s), intervals4join);
    // join new_first and second
    WorkingInterval result{new_first.interval.begin, second.interval.end,
                           new_first.working_time + second.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _06s);
    EXPECT_EQ(*intervals4join.begin(), result);
    EXPECT_EQ(intervals4join, (IntervalsSet{result, third, fourth}));
  }
  {
    // appending interval contains first
    WorkingInterval append{first.interval.begin - _05s,
                           first.interval.end + _05s, _01s};
    WorkingInterval new_first{append.interval.begin, append.interval.end,
                              append.working_time + first.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, second, third, fourth}));

    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _05s), intervals4join);
    // join new_first and second
    WorkingInterval result{new_first.interval.begin, second.interval.end,
                           new_first.working_time + second.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _06s);
    EXPECT_EQ(*intervals4join.begin(), result);
    EXPECT_EQ(intervals4join, (IntervalsSet{result, third, fourth}));
  }
  // work with second
  {
    // appending interval intersects with second (begin)
    WorkingInterval append{second.interval.begin - _05s,
                           second.interval.end - _05s, _03s};
    WorkingInterval new_second{append.interval.begin, second.interval.end,
                               append.working_time + second.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second, third, fourth}));

    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _05s), intervals4join);
    // join first and new_second
    WorkingInterval result{first.interval.begin, new_second.interval.end,
                           first.working_time + new_second.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _06s);
    EXPECT_EQ(*intervals4join.begin(), result);
    EXPECT_EQ(intervals4join, (IntervalsSet{result, third, fourth}));
  }
  {
    // appending interval intersects with second (end)
    WorkingInterval append{second.interval.begin + _05s,
                           second.interval.end + _05s, _03s};
    WorkingInterval new_second{second.interval.begin, append.interval.end,
                               second.working_time + append.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second, third, fourth}));

    // add interval inside new_second
    WorkingInterval inside{second.interval.begin + _05s,
                           new_second.interval.end - _05s, _01s};
    intervals4join.insert(inside);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    new_second.working_time += inside.working_time;
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second, third, fourth}));

    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _05s), intervals4join);
    // join new_second and third
    WorkingInterval result{new_second.interval.begin, third.interval.end,
                           new_second.working_time + third.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _06s);
    EXPECT_EQ(*std::next(intervals4join.begin()), result);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, result, fourth}));
  }
  {
    // appending interval contains second
    WorkingInterval append{second.interval.begin - _05s,
                           second.interval.end + _05s, _01s};
    WorkingInterval new_second{append.interval.begin, append.interval.end,
                               append.working_time + second.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second, third, fourth}));

    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _05s), intervals4join);
    // join first, new_second and third
    WorkingInterval result{
        first.interval.begin, third.interval.end,
        first.working_time + new_second.working_time + third.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _06s);
    EXPECT_EQ(*intervals4join.begin(), result);
    EXPECT_EQ(intervals4join, (IntervalsSet{result, fourth}));
  }
  // work with third
  {
    // appending interval intersects with third (end)
    WorkingInterval append{third.interval.begin + _05s,
                           third.interval.end + _05s, _04s};
    WorkingInterval new_third{third.interval.begin, append.interval.end,
                              third.working_time + append.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(std::next(intervals4join.begin())), new_third);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, new_third, fourth}));

    // add interval inside new_third
    WorkingInterval inside{new_third.interval.begin + _05s,
                           new_third.interval.end - _05s, _01s};
    intervals4join.insert(inside);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    new_third.working_time += inside.working_time;
    EXPECT_EQ(*std::next(std::next(intervals4join.begin())), new_third);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, new_third, fourth}));

    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _05s), intervals4join);
    // join new_third and fourth
    WorkingInterval result{new_third.interval.begin, fourth.interval.end,
                           new_third.working_time + fourth.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _06s);
    EXPECT_EQ(*std::next(std::next(intervals4join.begin())), result);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, result}));
  }
  {
    // appending interval contains third
    WorkingInterval append{third.interval.begin - _05s,
                           third.interval.end + _05s, _01s};
    WorkingInterval new_third{append.interval.begin, append.interval.end,
                              append.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(std::next(intervals4join.begin())), new_third);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, new_third, fourth}));

    EXPECT_EQ(ConvertToSeparateIntervals(intervals4join, _05s), intervals4join);
    // join second, new_third and fourth
    WorkingInterval result{
        second.interval.begin, fourth.interval.end,
        second.working_time + new_third.working_time + fourth.working_time};
    intervals4join = ConvertToSeparateIntervals(intervals4join, _06s);
    EXPECT_EQ(*std::next(intervals4join.begin()), result);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, result}));
  }
  // work with fourth (append only)
  {
    // appending interval intersects with fourth (begin)
    WorkingInterval append{fourth.interval.begin - _05s,
                           fourth.interval.end - _05s, _05s};
    WorkingInterval new_fourth{append.interval.begin, fourth.interval.end,
                               append.working_time + fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.rbegin(), new_fourth);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, third, new_fourth}));
  }
  {
    // appending interval intersects with fourth (end)
    WorkingInterval append{fourth.interval.begin + _05s,
                           fourth.interval.end + _05s, _05s};
    WorkingInterval new_fourth{fourth.interval.begin, append.interval.end,
                               fourth.working_time + append.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.rbegin(), new_fourth);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, third, new_fourth}));

    // add interval inside new_fourth
    WorkingInterval inside{fourth.interval.begin + _05s,
                           new_fourth.interval.end - _05s, _01s};
    intervals4join.insert(inside);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    new_fourth.working_time += inside.working_time;
    EXPECT_EQ(*intervals4join.rbegin(), new_fourth);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, third, new_fourth}));
  }
  {
    // appending interval contains fourth
    WorkingInterval append{fourth.interval.begin - _05s,
                           fourth.interval.end + _05s, _03s};
    WorkingInterval new_fourth{append.interval.begin, append.interval.end,
                               append.working_time + fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.rbegin(), new_fourth);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, third, new_fourth}));
  }
}

TEST(TestWorkingIntervals, CheckAppendIntersect2) {
  WorkingInterval first{time_05s, time_15s, _02s};
  WorkingInterval second{time_25s, time_35s, _01s};
  WorkingInterval third{time_45s, time_55s, _03s};
  WorkingInterval fourth{time_65s, time_75s, _01s};

  IntervalsSet intervals_set{fourth, first, third, second};

  // work with first and second
  {
    // appending interval intersects with first (end) and second (begin)
    WorkingInterval append{first.interval.end - _05s,
                           second.interval.begin + _05s, _04s};
    WorkingInterval new_first{
        first.interval.begin, second.interval.end,
        append.working_time + first.working_time + second.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, third, fourth}));
  }
  {
    // appending interval intersects with first (all) and second (begin)
    WorkingInterval append{first.interval.begin - _05s,
                           second.interval.begin + _05s, _10s};
    WorkingInterval new_first{
        append.interval.begin, second.interval.end,
        first.working_time + second.working_time + append.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, third, fourth}));
  }
  {
    // appending interval intersects with first (end) and second (all)
    WorkingInterval append{first.interval.end - _05s,
                           second.interval.end + _05s, _10s};
    WorkingInterval new_first{
        first.interval.begin, append.interval.end,
        first.working_time + second.working_time + append.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, third, fourth}));
  }
  {
    // appending interval contains first and second
    WorkingInterval append{first.interval.begin - _05s,
                           second.interval.end + _05s, _10s};
    WorkingInterval new_first{
        append.interval.begin, append.interval.end,
        first.working_time + second.working_time + append.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, third, fourth}));
  }
  // work with second and third
  {
    // appending interval intersects with second (end) and third (begin)
    WorkingInterval append{second.interval.end - _05s,
                           third.interval.begin + _05s, _04s};
    WorkingInterval new_second{
        second.interval.begin, third.interval.end,
        append.working_time + third.working_time + second.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second, fourth}));
  }
  {
    // appending interval intersects with second (all) and third (begin)
    WorkingInterval append{second.interval.begin - _05s,
                           third.interval.begin + _05s, _10s};
    WorkingInterval new_second{
        append.interval.begin, third.interval.end,
        append.working_time + third.working_time + second.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second, fourth}));
  }
  {
    // appending interval intersects with second (end) and third (all)
    WorkingInterval append{second.interval.end - _05s,
                           third.interval.end + _05s, _04s};
    WorkingInterval new_second{
        second.interval.begin, append.interval.end,
        append.working_time + third.working_time + second.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second, fourth}));
  }
  {
    // appending interval contains second and third
    WorkingInterval append{second.interval.begin - _05s,
                           third.interval.end + _05s, _05s};
    WorkingInterval new_second{
        append.interval.begin, append.interval.end,
        append.working_time + third.working_time + second.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second, fourth}));
  }
  // work with third and fourth
  {
    // appending interval intersects with third (end) and fourth (begin)
    WorkingInterval append{third.interval.end - _05s,
                           fourth.interval.begin + _05s, _04s};
    WorkingInterval new_third{
        third.interval.begin, fourth.interval.end,
        append.working_time + third.working_time + fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.rbegin(), new_third);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, new_third}));
  }
  {
    // appending interval intersects with third (all) and fourth (begin)
    WorkingInterval append{third.interval.begin - _05s,
                           fourth.interval.begin + _05s, _10s};
    WorkingInterval new_third{
        append.interval.begin, fourth.interval.end,
        append.working_time + third.working_time + fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.rbegin(), new_third);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, new_third}));
  }
  {
    // appending interval intersects with third (end) and fourth (all)
    WorkingInterval append{third.interval.end - _05s,
                           fourth.interval.end + _05s, _04s};
    WorkingInterval new_third{
        third.interval.begin, append.interval.end,
        append.working_time + third.working_time + fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.rbegin(), new_third);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, new_third}));
  }
  {
    // appending interval contains third and fourth
    WorkingInterval append{third.interval.begin - _05s,
                           fourth.interval.end + _05s, _05s};
    WorkingInterval new_third{
        append.interval.begin, append.interval.end,
        append.working_time + third.working_time + fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.rbegin(), new_third);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, second, new_third}));
  }
}

TEST(TestWorkingIntervals, CheckAppendIntersect3) {
  WorkingInterval first{time_05s, time_15s, _02s};
  WorkingInterval second{time_25s, time_35s, _01s};
  WorkingInterval third{time_45s, time_55s, _03s};
  WorkingInterval fourth{time_65s, time_75s, _01s};

  IntervalsSet intervals_set{fourth, first, third, second};

  // work with first, second and third
  {
    // appending interval intersects with first (end) and third (begin)
    WorkingInterval append{first.interval.end - _05s,
                           third.interval.begin + _05s, _04s};
    WorkingInterval new_first{first.interval.begin, third.interval.end,
                              append.working_time + first.working_time +
                                  second.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, fourth}));
  }
  {
    // appending interval intersects with first (all) and third (begin)
    WorkingInterval append{first.interval.begin - _05s,
                           third.interval.begin + _05s, _04s};
    WorkingInterval new_first{append.interval.begin, third.interval.end,
                              append.working_time + first.working_time +
                                  second.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, fourth}));
  }
  {
    // appending interval intersects with first (end) and third (all)
    WorkingInterval append{first.interval.end - _05s, third.interval.end + _05s,
                           _04s};
    WorkingInterval new_first{first.interval.begin, append.interval.end,
                              append.working_time + first.working_time +
                                  second.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, fourth}));
  }
  {
    // appending interval contains first, second and third
    WorkingInterval append{first.interval.begin - _05s,
                           third.interval.end + _05s, _04s};
    WorkingInterval new_first{append.interval.begin, append.interval.end,
                              append.working_time + first.working_time +
                                  second.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join, (IntervalsSet{new_first, fourth}));
  }
  // work with second, third and fourth
  {
    // appending interval intersects with second (end) and fourth (begin)
    WorkingInterval append{second.interval.end - _05s,
                           fourth.interval.begin + _05s, _04s};
    WorkingInterval new_second{second.interval.begin, fourth.interval.end,
                               append.working_time + fourth.working_time +
                                   second.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second}));
  }
  {
    // appending interval intersects with second (all) and fourth (begin)
    WorkingInterval append{second.interval.begin - _05s,
                           fourth.interval.begin + _05s, _05s};
    WorkingInterval new_second{append.interval.begin, fourth.interval.end,
                               append.working_time + fourth.working_time +
                                   second.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second}));
  }
  {
    // appending interval intersects with second (end) and fourth (all)
    WorkingInterval append{second.interval.end - _05s,
                           fourth.interval.end + _05s, _04s};
    WorkingInterval new_second{second.interval.begin, append.interval.end,
                               append.working_time + fourth.working_time +
                                   second.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second}));
  }
  {
    // appending interval contains second, third and fourth
    WorkingInterval append{second.interval.begin - _05s,
                           fourth.interval.end + _05s, _04s};
    WorkingInterval new_second{append.interval.begin, append.interval.end,
                               append.working_time + fourth.working_time +
                                   second.working_time + third.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*std::next(intervals4join.begin()), new_second);
    EXPECT_EQ(intervals4join, (IntervalsSet{first, new_second}));
  }
}

TEST(TestWorkingIntervals, CheckAppendIntersect4) {
  WorkingInterval first{time_05s, time_15s, _02s};
  WorkingInterval second{time_25s, time_35s, _01s};
  WorkingInterval third{time_45s, time_55s, _03s};
  WorkingInterval fourth{time_65s, time_75s, _01s};

  IntervalsSet intervals_set{fourth, first, third, second};

  {
    // appending interval intersects with first (end) and fourth (begin)
    WorkingInterval append{first.interval.end - _05s,
                           fourth.interval.begin + _05s, _04s};
    WorkingInterval new_first{first.interval.begin, fourth.interval.end,
                              append.working_time + first.working_time +
                                  second.working_time + third.working_time +
                                  fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join.size(), 1u);
  }
  {
    // appending interval intersects with first (all) and fourth (begin)
    WorkingInterval append{first.interval.begin - _05s,
                           fourth.interval.begin + _05s, _04s};
    WorkingInterval new_first{append.interval.begin, fourth.interval.end,
                              append.working_time + first.working_time +
                                  second.working_time + third.working_time +
                                  fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join.size(), 1u);
  }
  {
    // appending interval intersects with first (end) and fourth (all)
    WorkingInterval append{first.interval.end - _05s,
                           fourth.interval.end + _05s, _04s};
    WorkingInterval new_first{first.interval.begin, append.interval.end,
                              append.working_time + first.working_time +
                                  second.working_time + third.working_time +
                                  fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join.size(), 1u);
  }
  {
    // appending interval contains first, second, third and fourth
    WorkingInterval append{first.interval.begin - _05s,
                           fourth.interval.end + _05s, _04s};
    WorkingInterval new_first{append.interval.begin, append.interval.end,
                              append.working_time + first.working_time +
                                  second.working_time + third.working_time +
                                  fourth.working_time};

    auto intervals4join = ConvertToSeparateIntervals(intervals_set, {});
    intervals4join.insert(append);
    intervals4join = ConvertToSeparateIntervals(intervals4join, {});
    EXPECT_EQ(*intervals4join.begin(), new_first);
    EXPECT_EQ(intervals4join.size(), 1u);
  }
}

TEST(TestWorkingIntervals, GetLastWorkingInterval) {
  WorkingInterval first{time_05s, time_15s, _02s};
  WorkingInterval second{time_25s, time_35s, _01s};
  WorkingInterval third{time_45s, time_55s, _03s};
  WorkingInterval fourth{time_65s, time_75s, _01s};

  WorkingInterval result_full{first.interval.begin, fourth.interval.end,
                              first.working_time + second.working_time +
                                  third.working_time + fourth.working_time};
  {
    std::vector<WorkingInterval> intervals{first, second, third, fourth};

    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _06s).rbegin(), fourth);
    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _10s).rbegin(), fourth);
    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _11s).rbegin(),
              result_full);
  }

  third.interval.end += _04s;
  WorkingInterval result_34{third.interval.begin, fourth.interval.end,
                            third.working_time + fourth.working_time};
  {
    std::vector<WorkingInterval> intervals{first, second, third, fourth};

    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _06s).rbegin(), fourth);
    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _10s).rbegin(), result_34);
    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _11s).rbegin(),
              result_full);
  }

  second.interval.end += _04s;
  WorkingInterval result_234{
      second.interval.begin, fourth.interval.end,
      second.working_time + third.working_time + fourth.working_time};
  {
    std::vector<WorkingInterval> intervals{first, second, third, fourth};

    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _06s).rbegin(), fourth);
    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _10s).rbegin(),
              result_234);
    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _11s).rbegin(),
              result_full);
  }

  third.interval.end += _01s;
  {
    std::vector<WorkingInterval> intervals{first, second, third, fourth};

    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _06s).rbegin(), result_34);
    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _10s).rbegin(),
              result_234);
    EXPECT_EQ(*ConvertToSeparateIntervals(intervals, _11s).rbegin(),
              result_full);
  }
}
