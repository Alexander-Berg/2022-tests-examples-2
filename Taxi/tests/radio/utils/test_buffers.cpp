#include <gtest/gtest.h>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/utils/buffers.hpp"

namespace hejmdal::radio::blocks {

TEST(TestBuffersBlocks, TestDataBufferOutput) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(exit);

  {
    const double value = 3133.7;
    entry->DataIn(Meta::kNull, time::Now(), value);
    EXPECT_EQ(exit->LastValue(), value);
  }

  {
    const double value = 1337.0;
    entry->DataIn(Meta::kNull, time::Now(), value);
    EXPECT_EQ(exit->LastValue(), value);
  }
}

TEST(TestBuffersBlocks, TestStateBuffer) {
  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);

  {
    time::TimePoint tp = time::Now();
    const State state = State::kCritical;
    entry->StateIn(Meta::kNull, tp, state);
    EXPECT_EQ(test->LastTp(), tp);
    EXPECT_EQ(test->LastState(), State::kCritical);
  }

  {
    time::TimePoint tp = time::From<time::Milliseconds>(10);
    const State state = State::kNoData;
    entry->StateIn(Meta::kNull, tp, state);
    EXPECT_EQ(test->LastTp(), tp);
    EXPECT_EQ(test->LastState(), state);
  }
}

TEST(TestBuffersBlocks, TestBoundsBuffer) {
  auto entry = std::make_shared<BoundsEntryPoint>("");
  auto exit = std::make_shared<BoundsBuffer>("");
  entry->OnBoundsOut(exit);

  {
    time::TimePoint tp = time::Now();
    const double lower = -5;
    const double upper = 10;

    entry->BoundsIn(Meta::kNull, tp, lower, upper);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastLower(), lower);
    EXPECT_EQ(exit->LastUpper(), upper);
  }

  {
    time::TimePoint tp = time::From<time::Milliseconds>(10);
    const double lower = -100;
    const double upper = 1000;

    entry->BoundsIn(Meta::kNull, tp, lower, upper);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastLower(), lower);
    EXPECT_EQ(exit->LastUpper(), upper);
  }
}

}  // namespace hejmdal::radio::blocks
