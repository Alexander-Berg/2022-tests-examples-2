#include <gtest/gtest.h>

#include <userver/formats/json/inline.hpp>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/math/quantile.hpp"
#include "radio/blocks/utils/buffers.hpp"

namespace hejmdal::radio::blocks {

TEST(TestQuantileBlocks, TestFairQuantileSample) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto quantile = std::make_shared<FairQuantileSample>("", 0.5, 5);
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(quantile);
  quantile->OnDataOut(exit);

  entry->DataIn(Meta::kNull, time::Now(), 1);
  EXPECT_EQ(exit->LastValue(), 1);

  entry->DataIn(Meta::kNull, time::Now(), 2);
  EXPECT_EQ(exit->LastValue(), 2);

  entry->DataIn(Meta::kNull, time::Now(), 3);
  EXPECT_EQ(exit->LastValue(), 2);

  entry->DataIn(Meta::kNull, time::Now(), 4);
  EXPECT_EQ(exit->LastValue(), 3);

  entry->DataIn(Meta::kNull, time::Now(), 100);
  EXPECT_EQ(exit->LastValue(), 3);

  EXPECT_EQ(quantile->GetValue(0.0), 1);
  EXPECT_EQ(quantile->GetValue(0.1), 1);
  EXPECT_EQ(quantile->GetValue(0.2), 2);
  EXPECT_EQ(quantile->GetValue(0.3), 2);
  EXPECT_EQ(quantile->GetValue(0.4), 3);
  EXPECT_EQ(quantile->GetValue(0.5), 3);
  EXPECT_EQ(quantile->GetValue(0.6), 3);
  EXPECT_EQ(quantile->GetValue(0.7), 4);
  EXPECT_EQ(quantile->GetValue(0.8), 4);
  EXPECT_EQ(quantile->GetValue(0.9), 100);
  EXPECT_EQ(quantile->GetValue(1.0), 100);

  // last values are 1,2,3,4,100

  entry->DataIn(Meta::kNull, time::Now(), 3);  // 2,3,4,100,3
  EXPECT_EQ(exit->LastValue(), 3);

  entry->DataIn(Meta::kNull, time::Now(), 3);  // 3,4,100,3,3
  EXPECT_EQ(exit->LastValue(), 3);

  entry->DataIn(Meta::kNull, time::Now(), 4);  // 4,100,3,3,4
  EXPECT_EQ(exit->LastValue(), 4);

  entry->DataIn(Meta::kNull, time::Now(), -20);  // 100,3,3,4,-20
  EXPECT_EQ(exit->LastValue(), 3);

  entry->DataIn(Meta::kNull, time::Now(), -30);  // 3,3,4,-20,-30
  EXPECT_EQ(exit->LastValue(), 3);

  entry->DataIn(Meta::kNull, time::Now(), 0);  // 3,4,-20,-30,0
  EXPECT_EQ(exit->LastValue(), 0);
}

TEST(TestQuantileBlocks, TestFairQuantileWindow) {
  auto config = formats::json::MakeObject(
      "type", "fair_quantile_window", "id", "test", "window_sec", 60,
      "min_samples", 5, "max_samples", 8, "level", 0.5);

  auto entry = std::make_shared<DataEntryPoint>("");
  auto test_block = std::make_shared<FairQuantileWindow>(config);
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(test_block);
  test_block->OnDataOut(exit);

  auto now = std::chrono::system_clock::from_time_t(10);
  const auto k1Sec = time::Seconds{1};

  entry->DataIn(Meta::kNull, now, 4);
  EXPECT_EQ(exit->LastTp(), time::TimePoint{});

  entry->DataIn(Meta::kNull, now += k1Sec, 2);
  EXPECT_EQ(exit->LastTp(), time::TimePoint{});

  entry->DataIn(Meta::kNull, now += k1Sec, 4);
  EXPECT_EQ(exit->LastTp(), time::TimePoint{});

  entry->DataIn(Meta::kNull, now += k1Sec, 2);
  EXPECT_EQ(exit->LastTp(), time::TimePoint{});

  entry->DataIn(Meta::kNull, now += k1Sec, 1);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_DOUBLE_EQ(exit->LastValue(), 2.0);

  entry->DataIn(Meta::kNull, now += k1Sec, 8);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_DOUBLE_EQ(exit->LastValue(), 2.0);

  entry->DataIn(Meta::kNull, now += k1Sec, 10);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_DOUBLE_EQ(exit->LastValue(), 4.0);

  entry->DataIn(Meta::kNull, now += k1Sec, 15);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_DOUBLE_EQ(exit->LastValue(), 4.0);

  entry->DataIn(Meta::kNull, now += k1Sec, 25);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_DOUBLE_EQ(exit->LastValue(), 8.0);

  auto last_tp_before_pause = now;

  // test sliding time window
  entry->DataIn(Meta::kNull, now += 120 * k1Sec, 30);
  EXPECT_EQ(exit->LastTp(), last_tp_before_pause);
  EXPECT_DOUBLE_EQ(exit->LastValue(), 8.0);
}

}  // namespace hejmdal::radio::blocks
