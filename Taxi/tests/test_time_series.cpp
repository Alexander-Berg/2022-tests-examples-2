#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include <models/time_series.hpp>
#include <utils/time.hpp>

const std::string ts1_str = R"=(
{
  "timeseries": {
    "timestamps": [
      1574121600000,
      1574121660000,
      1574121720000,
      1574121780000,
      1574121840000,
      1574121900000
    ],
    "values": [
      17.0,
      23.0,
      25.0,
      23.0,
      20.0,
      16.0
    ]
  }
}
)=";

const std::string ts2_str = R"=(
{
  "timeseries": {
    "timestamps": [
      1574121600000,
      1574121660000,
      1574121700000,
      1574121720000,
      1574121780000,
      1574121840000,
      1574121900000
    ],
    "values": [
      17.0,
      23.0,
      "NaN",
      25.0,
      23.0,
      20.0,
      16.0
    ]
  }
}
)=";

const std::string ts3_str = R"=(
{
  "timeseries": {
    "timestamps": [
      1574121600000,
      1574121660000,
      1574121680000,
      1574121700000,
      1574121720000,
      1574121780000,
      1574121840000,
      1574121900000
    ],
    "values": [
      17.0,
      23.0,
      "NaN",
      "NaN",
      25.0,
      23.0,
      20.0,
      16.0
    ]
  }
}
)=";

const std::string ts4_str = R"=(
{
  "timeseries": {
    "timestamps": [
      1574121500000,
      1574121600000,
      1574121660000,
      1574121700000,
      1574121720000,
      1574121780000,
      1574121840000,
      1574121900000,
      1574122000000,
      1574122100000
    ],
    "values": [
      "NaN",
      17.0,
      23.0,
      "NaN",
      25.0,
      23.0,
      20.0,
      16.0,
      "NaN",
      "NaN"
    ]
  }
}
)=";

const std::string ts5_str = R"=(
{
  "timeseries": {
    "timestamps": [
      1574121500000,
      1574121600000,
      1574121660000,
      1574121700000,
      1574121720000,
      1574121780000,
      1574121840000,
      1574121900000,
      1574122000000,
      1574122100000
    ],
    "values": [
      "Infinity",
      17.0,
      23.0,
      "NaN",
      25.0,
      23.0,
      20.0,
      16.0,
      "Infinity",
      "NaN"
    ]
  }
}
)=";

const std::string ts_empty_str = R"=(
{
  "timeseries": {
    "timestamps": [
      1574121500000,
      1574121600000,
      1574121660000
    ],
    "values": [
      "NaN",
      "NaN",
      "NaN"
    ]
  }
}
)=";

const std::string ts_invalid_str = R"=(
{
  "timeseries": {
    "timestamps": [
      1574121500000,
      1574121600000,
      1574121660000
    ],
    "values": [
      "NaN",
      1.0,
      "invalid_value"
    ]
  }
}
)=";

namespace hejmdal::models {

TEST(TestTimeSeries, NaN) {
  TimeSeries expected;
  expected.Push({time::From<time::Milliseconds>(1574121600000), 17.0});
  expected.Push({time::From<time::Milliseconds>(1574121660000), 23.0});
  expected.Push({time::From<time::Milliseconds>(1574121720000), 25.0});
  expected.Push({time::From<time::Milliseconds>(1574121780000), 23.0});
  expected.Push({time::From<time::Milliseconds>(1574121840000), 20.0});
  expected.Push({time::From<time::Milliseconds>(1574121900000), 16.0});

  auto ts1 = formats::json::FromString(ts1_str);
  EXPECT_EQ(expected, TimeSeries::FromJson(ts1));

  auto ts2 = formats::json::FromString(ts2_str);
  EXPECT_EQ(expected, TimeSeries::FromJson(ts2));

  auto ts3 = formats::json::FromString(ts3_str);
  EXPECT_EQ(expected, TimeSeries::FromJson(ts3));

  auto ts4 = formats::json::FromString(ts4_str);
  EXPECT_EQ(expected, TimeSeries::FromJson(ts4));

  auto ts5 = formats::json::FromString(ts5_str);
  EXPECT_EQ(expected, TimeSeries::FromJson(ts5));

  auto ts_empty = formats::json::FromString(ts_empty_str);
  EXPECT_TRUE(TimeSeries::FromJson(ts_empty).empty());

  auto ts_invalid = formats::json::FromString(ts_invalid_str);
  EXPECT_THROW(auto ts = TimeSeries::FromJson(ts_invalid), except::Error);
}

}  // namespace hejmdal::models
