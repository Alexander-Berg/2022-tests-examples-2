#include <gtest/gtest.h>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/utils/buffers.hpp"
#include "radio/blocks/utils/mappers.hpp"

namespace hejmdal::radio::blocks {

TEST(TestMappersBlocks, TestDataMapper) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto mapper =
      std::make_shared<DataMapper>([](double value_) { return value_ * 10; });
  auto exit = std::make_shared<DataBuffer>("");
  entry->OnDataOut(mapper);
  mapper->OnDataOut(exit);

  {
    const double value = 3133.7;
    entry->DataIn(Meta::kNull, time::Now(), value);
    EXPECT_EQ(exit->LastValue(), 31337);
  }
}

TEST(TestUtilsBlocks, TestStateMapper) {
  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = std::make_shared<StateMapper>([](const State& it) -> const State {
    if (it == State::kNoData) return State::kOk;
    if (it == State::kOk) return State::kOk;
    if (it == State::kWarn) return State::kCritical;
    if (it == State::kError) return State::kCritical;
    if (it == State::kCritical) return State::kCritical;
    return State::kNoData;
  });
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  auto meta = Meta::kNull;
  auto tp = time::Now();
  {
    // buffer is empty
    EXPECT_EQ(exit->LastTp(), time::From<time::Milliseconds>(0));
    EXPECT_EQ(exit->LastState(), State::kNoData);
  }

  {
    entry->StateIn(meta, tp, State::kWarn);
    EXPECT_EQ(exit->LastState(), State::kCritical);

    entry->StateIn(meta, tp, State::kNoData);
    EXPECT_EQ(exit->LastState(), State::kOk);

    entry->StateIn(meta, tp, State::kError);
    EXPECT_EQ(exit->LastState(), State::kCritical);

    entry->StateIn(meta, tp, State::kOk);
    EXPECT_EQ(exit->LastState(), State::kOk);

    entry->StateIn(meta, tp, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
  }
}

}  // namespace hejmdal::radio::blocks
