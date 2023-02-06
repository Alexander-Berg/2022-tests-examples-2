#include <gtest/gtest.h>

#include <radio/blocks/block_factory.hpp>
#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/math/quartile_bounds.hpp>
#include <radio/blocks/utils/buffers.hpp>

namespace hejmdal::radio::blocks {

namespace {

time::TimePoint FromMillis(std::int64_t milliseconds_count) {
  return time::From<time::Milliseconds>(milliseconds_count);
}

}  // namespace

TEST(TestQuartileBoundsBlocks, TestMADBoundsGeneratorSample) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto test = std::make_shared<MADBoundsGeneratorSample>("", 10, 3.0);
  auto exit = std::make_shared<BoundsBuffer>("");
  entry->OnDataOut(test);
  test->OnBoundsOut(exit);

  {
    entry->DataIn(Meta::kNull, time::Now(), 1);
    entry->DataIn(Meta::kNull, time::Now(), 2);
    entry->DataIn(Meta::kNull, time::Now(), 3);
    entry->DataIn(Meta::kNull, time::Now(), 4);
    entry->DataIn(Meta::kNull, time::Now(), 5);
    entry->DataIn(Meta::kNull, time::Now(), 6);
    entry->DataIn(Meta::kNull, time::Now(), 7);
    entry->DataIn(Meta::kNull, time::Now(), 8);
    entry->DataIn(Meta::kNull, time::Now(), 9);

    EXPECT_EQ(exit->LastLower(), std::numeric_limits<double>::lowest());
    EXPECT_EQ(exit->LastUpper(), std::numeric_limits<double>::max());
  }

  {
    entry->DataIn(Meta::kNull, FromMillis(100), 10);

    EXPECT_EQ(exit->LastTp(), FromMillis(100));
    EXPECT_EQ(exit->LastLower(), -3);
    EXPECT_EQ(exit->LastUpper(), 15);
  }

  {
    //второй раз прогоняем на тех же данных + 100
    entry->DataIn(Meta::kNull, time::Now(), 100 + 1);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 2);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 3);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 4);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 5);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 6);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 7);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 8);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 9);
    entry->DataIn(Meta::kNull, FromMillis(200), 100 + 10);

    EXPECT_EQ(exit->LastTp(), FromMillis(200));
    //это нормально, что границы будут отличаться, т.к. в этот проход все еще
    //влияет медиана от первого прохода
    EXPECT_EQ(exit->LastLower(), 100 + -3 - 3);
    EXPECT_EQ(exit->LastUpper(), 100 + 15 + 3);
  }

  {
    //третий раз прогоняем на тех же данных + 100
    entry->DataIn(Meta::kNull, time::Now(), 100 + 10);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 9);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 8);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 7);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 6);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 5);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 4);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 3);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 2);
    entry->DataIn(Meta::kNull, FromMillis(300), 100 + 1);

    EXPECT_EQ(exit->LastTp(), FromMillis(300));
    //границы должны совпадать (+100) с первым проходом
    EXPECT_EQ(exit->LastLower(), 100 + -3);
    EXPECT_EQ(exit->LastUpper(), 100 + 15);
  }
}

TEST(TestQuartileBoundsBlocks, TestIDQBoundsGeneratorSample) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto test = std::make_shared<IDQBoundsGeneratorSample>("", 10, 3.0, 1.0);
  auto exit = std::make_shared<BoundsBuffer>("");
  entry->OnDataOut(test);
  test->OnBoundsOut(exit);

  {
    entry->DataIn(Meta::kNull, time::Now(), 1);
    entry->DataIn(Meta::kNull, time::Now(), 2);
    entry->DataIn(Meta::kNull, time::Now(), 3);
    entry->DataIn(Meta::kNull, time::Now(), 4);
    entry->DataIn(Meta::kNull, time::Now(), 5);
    entry->DataIn(Meta::kNull, time::Now(), 6);
    entry->DataIn(Meta::kNull, time::Now(), 7);
    entry->DataIn(Meta::kNull, time::Now(), 8);
    entry->DataIn(Meta::kNull, time::Now(), 9);

    EXPECT_EQ(exit->LastLower(), std::numeric_limits<double>::lowest());
    EXPECT_EQ(exit->LastUpper(), std::numeric_limits<double>::max());
  }

  {
    entry->DataIn(Meta::kNull, FromMillis(100), 10);

    EXPECT_EQ(exit->LastTp(), FromMillis(100));
    EXPECT_EQ(exit->LastLower(), -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 21 + 1);
  }

  {
    //второй раз прогоняем на тех же данных + 100
    entry->DataIn(Meta::kNull, time::Now(), 100 + 10);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 9);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 8);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 7);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 6);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 5);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 4);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 3);
    entry->DataIn(Meta::kNull, time::Now(), 100 + 2);
    entry->DataIn(Meta::kNull, FromMillis(300), 100 + 1);

    EXPECT_EQ(exit->LastTp(), FromMillis(300));
    //границы должны совпадать (+100) с первым проходом
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);
  }
}

TEST(TestQuartileBoundsBlocks, TestIDQBoundsGeneratorWindow) {
  auto config = formats::json::MakeObject(
      "id", "test", "type", "IDQ_bounds_generator_window", "coeff", 3.0,
      "base_term", 1.0, "min_samples", 10, "max_samples", 1000, "window_sec",
      10);

  auto entry = std::make_shared<DataEntryPoint>("");
  auto test = BlockFactory::CreateBlock(config);
  auto exit = std::make_shared<BoundsBuffer>("");
  entry->OnDataOut(test);
  test->OnBoundsOut(exit);

  auto now = time::From<time::Seconds>(1);
  static const auto k1Sec = time::Seconds{1};

  {
    entry->DataIn(Meta::kNull, now += k1Sec, 1);
    entry->DataIn(Meta::kNull, now += k1Sec, 2);
    entry->DataIn(Meta::kNull, now += k1Sec, 3);
    entry->DataIn(Meta::kNull, now += k1Sec, 4);
    entry->DataIn(Meta::kNull, now += k1Sec, 5);
    entry->DataIn(Meta::kNull, now += k1Sec, 6);
    entry->DataIn(Meta::kNull, now += k1Sec, 7);
    entry->DataIn(Meta::kNull, now += k1Sec, 8);
    entry->DataIn(Meta::kNull, now += k1Sec, 9);

    EXPECT_EQ(exit->LastLower(), std::numeric_limits<double>::lowest());
    EXPECT_EQ(exit->LastUpper(), std::numeric_limits<double>::max());
  }

  {
    entry->DataIn(Meta::kNull, now += k1Sec, 10);

    EXPECT_EQ(exit->LastTp(), now);
    EXPECT_EQ(exit->LastLower(), -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 21 + 1);
  }

  {
    //второй раз прогоняем на тех же данных + 100
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 10);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 9);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 8);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 7);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 6);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 5);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 4);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 3);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 2);
    entry->DataIn(Meta::kNull, now += k1Sec, 100 + 1);

    EXPECT_EQ(exit->LastTp(), now);
    //границы должны совпадать (+100) с первым проходом
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);
  }

  {
    auto old_now = now;
    now += 4 * k1Sec;

    // в окне меньше min_samples данных -- не обновляем выходы
    entry->DataIn(Meta::kNull, now += k1Sec, 1);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 2);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 3);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 4);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 5);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 6);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 7);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 8);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 9);

    EXPECT_EQ(exit->LastTp(), old_now);
    EXPECT_EQ(exit->LastLower(), 100 + -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 100 + 21 + 1);

    entry->DataIn(Meta::kNull, now += k1Sec, 10);
    // в окне снова достаточно данных, на выходах новые границы
    EXPECT_EQ(exit->LastTp(), now);
    EXPECT_EQ(exit->LastLower(), -9 - 1);
    EXPECT_EQ(exit->LastUpper(), 21 + 1);
  }
}

}  // namespace hejmdal::radio::blocks
