#include <gtest/gtest.h>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/state.hpp"
#include "radio/blocks/utils/buffers.hpp"
#include "radio/blocks/utils/filters.hpp"

namespace hejmdal::radio::blocks {

namespace {

time::TimePoint FromMillis(std::int64_t milliseconds_count) {
  return time::From<time::Milliseconds>(milliseconds_count);
}

}  // namespace

TEST(TestFiltersBlocks, TestStateSwitch) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto entry_state = std::make_shared<StateEntryPoint>("");
  auto test = std::make_shared<StateSwitch>("", State::kOk);
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(test);
  entry_state->OnStateOut(test);
  test->OnDataOut(exit);

  auto meta = Meta::kNull;

  {
    // buffer is empty
    EXPECT_EQ(exit->LastTp(), FromMillis(0));
    EXPECT_EQ(exit->LastValue(), 0.0);
  }

  {
    entry->DataIn(meta, FromMillis(100), 10);
    EXPECT_EQ(exit->LastTp(), FromMillis(100));
    EXPECT_EQ(exit->LastValue(), 10);

    entry->DataIn(meta, FromMillis(200), 20);
    entry->DataIn(meta, FromMillis(300), 30);
    entry->DataIn(meta, FromMillis(400), 40);
    entry->DataIn(meta, FromMillis(500), 50);
    EXPECT_EQ(exit->LastTp(), FromMillis(500));
    EXPECT_EQ(exit->LastValue(), 50);
  }

  {
    // turning off switch
    entry_state->StateIn(meta, FromMillis(600), State::Value::kNoData);
    entry->DataIn(meta, FromMillis(600), 60);
    entry->DataIn(meta, FromMillis(700), 70);
    EXPECT_EQ(exit->LastTp(), FromMillis(500));
    EXPECT_EQ(exit->LastValue(), 50);

    entry_state->StateIn(meta, FromMillis(600), State::Value::kWarn);
    entry->DataIn(meta, FromMillis(700), 70);
    EXPECT_EQ(exit->LastTp(), FromMillis(500));
    EXPECT_EQ(exit->LastValue(), 50);

    entry_state->StateIn(meta, FromMillis(600), State::Value::kError);
    entry->DataIn(meta, FromMillis(700), 70);
    EXPECT_EQ(exit->LastTp(), FromMillis(500));
    EXPECT_EQ(exit->LastValue(), 50);

    entry_state->StateIn(meta, FromMillis(600), State::Value::kCritical);
    entry->DataIn(meta, FromMillis(700), 70);
    EXPECT_EQ(exit->LastTp(), FromMillis(500));
    EXPECT_EQ(exit->LastValue(), 50);
  }

  {
    // turning on switch
    entry_state->StateIn(meta, FromMillis(600), State::Value::kOk);
    entry->DataIn(meta, FromMillis(700), 70);
    EXPECT_EQ(exit->LastTp(), FromMillis(700));
    EXPECT_EQ(exit->LastValue(), 70);
  }
}

TEST(TestFiltersBlocks, TestBoundsDataFilter) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto entry_bounds = std::make_shared<BoundsEntryPoint>("");
  auto test = std::make_shared<BoundsDataFilter>("");
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(test);
  entry_bounds->OnBoundsOut(test);
  test->OnDataOut(exit);

  auto meta = Meta::kNull;

  {
    // buffer is empty
    EXPECT_EQ(exit->LastTp(), FromMillis(0));
    EXPECT_EQ(exit->LastValue(), 0.0);
  }

  {
    entry->DataIn(meta, FromMillis(100), 10);
    EXPECT_EQ(exit->LastTp(), FromMillis(100));
    EXPECT_EQ(exit->LastValue(), 10);

    entry->DataIn(meta, FromMillis(200), 20);
    entry->DataIn(meta, FromMillis(300), 30);
    entry->DataIn(meta, FromMillis(400), 40);
    entry->DataIn(meta, FromMillis(500), 50);
    EXPECT_EQ(exit->LastTp(), FromMillis(500));
    EXPECT_EQ(exit->LastValue(), 50);
  }

  {
    // narrowing bounds
    entry_bounds->BoundsIn(meta, FromMillis(600), 10, 20);
    entry->DataIn(meta, FromMillis(600), 60);
    entry->DataIn(meta, FromMillis(700), 70);
    EXPECT_EQ(exit->LastTp(), FromMillis(500));
    EXPECT_EQ(exit->LastValue(), 50);

    entry->DataIn(meta, FromMillis(800), 15);
    EXPECT_EQ(exit->LastTp(), FromMillis(800));
    EXPECT_EQ(exit->LastValue(), 15);
  }

  {
    // expanding bounds
    entry_bounds->BoundsIn(meta, FromMillis(900), 10, 200);
    entry->DataIn(meta, FromMillis(1000), 70);
    EXPECT_EQ(exit->LastTp(), FromMillis(1000));
    EXPECT_EQ(exit->LastValue(), 70);
  }
}

}  // namespace hejmdal::radio::blocks
