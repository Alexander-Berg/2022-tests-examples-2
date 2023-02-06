#include <gtest/gtest.h>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/utils/sample_buffers.hpp"

namespace hejmdal::radio::blocks {

namespace {

time::TimePoint FromMillis(std::int64_t milliseconds_count) {
  return time::From<time::Milliseconds>(milliseconds_count);
}

}  // namespace

TEST(TestSampleBuffers, TestDataBufferSample) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto test = std::make_shared<DataBufferSample>(3, "test_data");
  entry->OnDataOut(test);

  {
    auto series_vector = test->ExtractData();
    EXPECT_EQ(series_vector.size(), 0);
  }

  {
    entry->DataIn(Meta::kNull, FromMillis(100), 1);
    entry->DataIn(Meta::kNull, FromMillis(200), 2);

    auto series = test->ExtractData();
    EXPECT_EQ(series.size(), 2);
    EXPECT_EQ(series[0].GetTime(), FromMillis(100));
    EXPECT_EQ(series[0].GetValue(), 1.0);
    EXPECT_EQ(series[1].GetTime(), FromMillis(200));
    EXPECT_EQ(series[1].GetValue(), 2.0);
  }

  {
    auto series = test->ExtractData();
    EXPECT_EQ(series.size(), 0);
  }

  {
    entry->DataIn(Meta::kNull, FromMillis(100), 1);
    entry->DataIn(Meta::kNull, FromMillis(200), 2);
    entry->DataIn(Meta::kNull, FromMillis(300), 3);
    entry->DataIn(Meta::kNull, FromMillis(400), 4);
    entry->DataIn(Meta::kNull, FromMillis(500), 5);
    entry->DataIn(Meta::kNull, FromMillis(600), 6);
    entry->DataIn(Meta::kNull, FromMillis(700), 7);

    auto series = test->ExtractData();
    EXPECT_EQ(series.size(), 3);
    EXPECT_EQ(series[0].GetTime(), FromMillis(500));
    EXPECT_EQ(series[0].GetValue(), 5.0);
    EXPECT_EQ(series[1].GetTime(), FromMillis(600));
    EXPECT_EQ(series[1].GetValue(), 6.0);
    EXPECT_EQ(series[2].GetTime(), FromMillis(700));
    EXPECT_EQ(series[2].GetValue(), 7.0);
  }

  {
    auto series = test->ExtractData();
    EXPECT_EQ(series.size(), 0);
  }

  {
    entry->DataIn(Meta::kNull, FromMillis(100), 1);
    entry->DataIn(Meta::kNull, FromMillis(200), 2);
    entry->DataIn(Meta::kNull, FromMillis(300), 3);
    entry->DataIn(Meta::kNull, FromMillis(400), 4);
    entry->DataIn(Meta::kNull, FromMillis(500), 5);
    entry->DataIn(Meta::kNull, FromMillis(600), 6);
    entry->DataIn(Meta::kNull, FromMillis(700), 7);

    auto series_map = test->ExtractTimeSeries();
    EXPECT_EQ(series_map.size(), 1);
    auto& [name, series] = *series_map.begin();
    EXPECT_EQ(name, "test_data");
    EXPECT_EQ(series.size(), 3);

    int i = 0;
    for (const auto& sensor_val : series) {
      EXPECT_EQ(sensor_val.GetTime(), FromMillis(500 + i * 100));
      EXPECT_DOUBLE_EQ(sensor_val.GetValue(), 5.0 + i);
      i++;
    }
  }
}

TEST(TestSampleBuffers, TestStateBufferSample) {
  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = std::make_shared<StateBufferSample>(3, "test_state");
  entry->OnStateOut(test);

  {
    auto series = test->ExtractState();
    EXPECT_EQ(series.size(), 0);
  }

  {
    entry->StateIn(Meta::kNull, FromMillis(100), State::Value::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(200), State::Value::kCritical);

    auto series = test->ExtractState();
    EXPECT_EQ(series.size(), 2);
    EXPECT_EQ(series[0].GetTime(), FromMillis(100));
    EXPECT_EQ(series[0].GetValue(), State::Value::kNoData);
    EXPECT_EQ(series[1].GetTime(), FromMillis(200));
    EXPECT_EQ(series[1].GetValue(), State::Value::kCritical);
  }

  {
    auto series = test->ExtractState();
    EXPECT_EQ(series.size(), 0);
  }

  {
    entry->StateIn(Meta::kNull, FromMillis(100), State::Value::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(200), State::Value::kOk);
    entry->StateIn(Meta::kNull, FromMillis(300), State::Value::kWarn);
    entry->StateIn(Meta::kNull, FromMillis(400), State::Value::kError);
    entry->StateIn(Meta::kNull, FromMillis(500), State::Value::kCritical);
    entry->StateIn(Meta::kNull, FromMillis(600), State::Value::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(700), State::Value::kOk);

    auto series = test->ExtractState();
    EXPECT_EQ(series.size(), 3);
    EXPECT_EQ(series[0].GetTime(), FromMillis(500));
    EXPECT_EQ(series[0].GetValue(), State::Value::kCritical);
    EXPECT_EQ(series[1].GetTime(), FromMillis(600));
    EXPECT_EQ(series[1].GetValue(), State::Value::kNoData);
    EXPECT_EQ(series[2].GetTime(), FromMillis(700));
    EXPECT_EQ(series[2].GetValue(), State::Value::kOk);
  }

  {
    auto series = test->ExtractState();
    EXPECT_EQ(series.size(), 0);
  }

  {
    entry->StateIn(Meta::kNull, FromMillis(100), State::Value::kNoData);
    entry->StateIn(Meta::kNull, FromMillis(200), State::Value::kOk);
    entry->StateIn(Meta::kNull, FromMillis(300), State::Value::kWarn);
    entry->StateIn(Meta::kNull, FromMillis(400), State::Value::kError);
    entry->StateIn(Meta::kNull, FromMillis(500), State::Value::kOk);
    entry->StateIn(Meta::kNull, FromMillis(600), State::Value::kWarn);
    entry->StateIn(Meta::kNull, FromMillis(700), State::Value::kError);

    auto series_map = test->ExtractTimeSeries();
    EXPECT_EQ(series_map.size(), 1);
    auto& [name, series] = *series_map.begin();
    EXPECT_EQ(name, "test_state");
    EXPECT_EQ(series.size(), 3);

    int i = 0;
    for (const auto& sensor_val : series) {
      EXPECT_EQ(sensor_val.GetTime(), FromMillis(500 + i * 100));
      EXPECT_DOUBLE_EQ(sensor_val.GetValue(), 0. + i);
      i++;
    }
  }
}

TEST(TestSampleBuffers, TestBoundsBufferSample) {
  auto entry = std::make_shared<BoundsEntryPoint>("");
  auto test = std::make_shared<BoundsBufferSample>(3, "test_bounds");
  entry->OnBoundsOut(test);

  {
    auto series = test->ExtractBounds();
    EXPECT_EQ(series.size(), 0);
  }

  {
    entry->BoundsIn(Meta::kNull, FromMillis(100), 1, 10);
    entry->BoundsIn(Meta::kNull, FromMillis(200), 2, 20);

    auto series = test->ExtractBounds();
    EXPECT_EQ(series.size(), 2);
    EXPECT_EQ(series[0].GetTime(), FromMillis(100));
    EXPECT_EQ(series[0].GetValue().lower, 1.0);
    EXPECT_EQ(series[0].GetValue().upper, 10.0);
    EXPECT_EQ(series[1].GetTime(), FromMillis(200));
    EXPECT_EQ(series[1].GetValue().lower, 2.0);
    EXPECT_EQ(series[1].GetValue().upper, 20.0);
  }

  {
    auto series = test->ExtractBounds();
    EXPECT_EQ(series.size(), 0);
  }

  {
    entry->BoundsIn(Meta::kNull, FromMillis(100), 1, 10);
    entry->BoundsIn(Meta::kNull, FromMillis(200), 2, 20);
    entry->BoundsIn(Meta::kNull, FromMillis(300), 3, 30);
    entry->BoundsIn(Meta::kNull, FromMillis(400), 4, 40);
    entry->BoundsIn(Meta::kNull, FromMillis(500), 5, 50);
    entry->BoundsIn(Meta::kNull, FromMillis(600), 6, 60);
    entry->BoundsIn(Meta::kNull, FromMillis(700), 7, 70);

    auto series = test->ExtractBounds();
    EXPECT_EQ(series.size(), 3);
    EXPECT_EQ(series[0].GetTime(), FromMillis(500));
    EXPECT_EQ(series[0].GetValue().lower, 5.0);
    EXPECT_EQ(series[0].GetValue().upper, 50.0);
    EXPECT_EQ(series[1].GetTime(), FromMillis(600));
    EXPECT_EQ(series[1].GetValue().lower, 6.0);
    EXPECT_EQ(series[1].GetValue().upper, 60.0);
    EXPECT_EQ(series[2].GetTime(), FromMillis(700));
    EXPECT_EQ(series[2].GetValue().lower, 7.0);
    EXPECT_EQ(series[2].GetValue().upper, 70.0);
  }

  {
    auto series = test->ExtractBounds();
    EXPECT_EQ(series.size(), 0);
  }

  {
    entry->BoundsIn(Meta::kNull, FromMillis(100), 1, 10);
    entry->BoundsIn(Meta::kNull, FromMillis(200), 2, 20);
    entry->BoundsIn(Meta::kNull, FromMillis(300), 3, 30);
    entry->BoundsIn(Meta::kNull, FromMillis(400), 4, 40);
    entry->BoundsIn(Meta::kNull, FromMillis(500), 5, 50);
    entry->BoundsIn(Meta::kNull, FromMillis(600), 6, 60);
    entry->BoundsIn(Meta::kNull, FromMillis(700), 7, 70);

    auto series_map = test->ExtractTimeSeries();
    EXPECT_EQ(series_map.size(), 2);
    auto& lower_series = series_map["test_bounds_lower_bound"];
    auto& upper_series = series_map["test_bounds_upper_bound"];
    EXPECT_EQ(lower_series.size(), 3);
    EXPECT_EQ(upper_series.size(), 3);

    int i = 0;
    for (const auto& sensor_val : lower_series) {
      EXPECT_EQ(sensor_val.GetTime(), FromMillis(500 + i * 100));
      EXPECT_DOUBLE_EQ(sensor_val.GetValue(), 5. + i);
      i++;
    }
    i = 0;
    for (const auto& sensor_val : upper_series) {
      EXPECT_EQ(sensor_val.GetTime(), FromMillis(500 + i * 100));
      EXPECT_DOUBLE_EQ(sensor_val.GetValue(), 50. + i * 10);
      i++;
    }
  }
}

}  // namespace hejmdal::radio::blocks
