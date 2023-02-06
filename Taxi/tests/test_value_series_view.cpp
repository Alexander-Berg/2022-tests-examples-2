#include <gtest/gtest.h>

#include <models/time_series.hpp>
#include <models/time_series_view.hpp>
#include <utils/time.hpp>

namespace hejmdal {

const auto min = time::Minutes(1);
const auto sec = time::Seconds(1);

double CheckRangeForward(const models::TimeSeriesView& view,
                         std::size_t check_size, double start_val) {
  std::size_t size = 0;
  double check_val = start_val;
  for (const auto& val : view) {
    EXPECT_DOUBLE_EQ(val.GetValue(), check_val);
    check_val += 1.;
    size++;
  }
  EXPECT_EQ(size, check_size);
  EXPECT_EQ(view.size(), size);
  return check_val - 1;
}

double CheckRangeBackward(const models::TimeSeriesView& view,
                          std::size_t check_size, double end_val) {
  std::size_t size = 0;
  double check_val = end_val;
  auto iter = view.end();
  do {
    if (view.empty()) break;
    --iter;
    EXPECT_DOUBLE_EQ(iter->GetValue(), check_val);
    check_val -= 1.;
    size++;
  } while (iter != view.begin());

  EXPECT_EQ(size, check_size);
  EXPECT_EQ(view.size(), size);
  return check_val + 1;
}

void CheckRange(const models::TimeSeriesView& view, std::size_t check_size,
                double start_val) {
  auto last_val = CheckRangeForward(view, check_size, start_val);
  auto first_val = CheckRangeBackward(view, check_size, last_val);
  EXPECT_EQ(first_val, start_val);
}

void CheckRange(const models::TimeSeries& series, const time::TimeRange& range,
                std::size_t check_size, double start_val) {
  models::TimeSeriesView view;
  view.Add(series, range);
  CheckRange(view, check_size, start_val);
}

TEST(TestTimeSeriesView, AddSingleTimeSeries) {
  auto start_ts = time::Clock::now() - time::Minutes(1000);
  auto end_ts = start_ts + min;

  models::TimeSeries series;

  CheckRange(series, time::TimeRange(start_ts, end_ts), 0u, 1.);

  series.Push(models::SensorValue(start_ts, 1.));

  CheckRange(series, time::TimeRange(start_ts, end_ts), 1u, 1.);

  series.Push(models::SensorValue(start_ts + sec * 30, 2.));
  series.Push(models::SensorValue(end_ts, 3.));

  CheckRange(series, time::TimeRange(start_ts, end_ts), 2u, 1.);
  CheckRange(series, time::TimeRange(start_ts, end_ts + min), 3u, 1.);
  CheckRange(series, time::TimeRange(end_ts, end_ts + min), 1u, 3.);
}

TEST(TestTimeSeriesView, AddMultiTimeSeries) {
  auto start_ts = time::Clock::now();
  auto end_ts = start_ts + min;

  models::TimeSeries series1;
  series1.Push(models::SensorValue(start_ts, 1.));
  series1.Push(models::SensorValue(start_ts + sec, 2.));
  series1.Push(models::SensorValue(start_ts + sec * 2, 3.));
  models::TimeSeries series2;
  series2.Push(models::SensorValue(start_ts + sec * 3, 4.));
  series2.Push(models::SensorValue(start_ts + sec * 4, 5.));
  series2.Push(models::SensorValue(start_ts + sec * 5, 6.));
  models::TimeSeries series3;
  series3.Push(models::SensorValue(start_ts + sec * 6, 7.));
  series3.Push(models::SensorValue(start_ts + sec * 7, 8.));
  series3.Push(models::SensorValue(start_ts + sec * 8, 9.));

  {
    time::TimeRange full_range(start_ts, end_ts);
    models::TimeSeriesView view;
    view.Add(series1, full_range);
    view.Add(series2, full_range);
    view.Add(series3, full_range);

    CheckRange(view, 9u, 1.);
  }
  {
    time::TimeRange range(start_ts, start_ts + sec * 5);
    models::TimeSeriesView view;
    view.Add(series1, range);
    view.Add(series2, range);
    view.Add(series3, range);

    CheckRange(view, 5u, 1.);
  }
  {
    time::TimeRange range(start_ts, start_ts + sec * 6);
    models::TimeSeriesView view;
    view.Add(series1, range);
    view.Add(series2, range);
    view.Add(series3, range);

    CheckRange(view, 6u, 1.);
  }
  {
    time::TimeRange range(start_ts + sec, start_ts + sec * 7);
    models::TimeSeriesView view;
    view.Add(series1, range);
    view.Add(series2, range);
    view.Add(series3, range);

    CheckRange(view, 6u, 2.);
  }
  {
    time::TimeRange range(start_ts + sec * 3, start_ts + sec * 9);
    models::TimeSeriesView view;
    view.Add(series1, range);
    view.Add(series2, range);
    view.Add(series3, range);

    CheckRange(view, 6u, 4.);
  }
}

TEST(TestTimeSeriesView, TestBeginEndCtor) {
  auto start_ts = time::Clock::now();
  auto end_ts = start_ts + min;

  models::TimeSeries series1;
  series1.Push(models::SensorValue(start_ts, 1.));
  series1.Push(models::SensorValue(start_ts + sec, 2.));
  series1.Push(models::SensorValue(start_ts + sec * 2, 3.));
  models::TimeSeries series2;
  series2.Push(models::SensorValue(start_ts + sec * 3, 4.));
  series2.Push(models::SensorValue(start_ts + sec * 4, 5.));
  series2.Push(models::SensorValue(start_ts + sec * 5, 6.));
  models::TimeSeries series3;
  series3.Push(models::SensorValue(start_ts + sec * 6, 7.));
  series3.Push(models::SensorValue(start_ts + sec * 7, 8.));
  series3.Push(models::SensorValue(start_ts + sec * 8, 9.));

  time::TimeRange full_range(start_ts, end_ts);
  models::TimeSeriesView view;
  view.Add(series1, full_range);
  view.Add(series2, full_range);
  view.Add(series3, full_range);

  {
    auto new_view = models::TimeSeriesView(view.begin(), view.end());
    EXPECT_DOUBLE_EQ(new_view.front().GetValue(), view.front().GetValue());
    EXPECT_DOUBLE_EQ(new_view.back().GetValue(), view.back().GetValue());
  }
  {
    auto begin = view.begin() + 2;
    auto end = view.end() - 1;
    auto new_view = models::TimeSeriesView(begin, end);
    auto new_iter = new_view.begin();
    for (auto iter = begin; iter != end; ++iter, ++new_iter) {
      EXPECT_DOUBLE_EQ(iter->GetValue(), new_iter->GetValue());
    }
  }
}

}  // namespace hejmdal
