#include <gtest/gtest.h>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/utils/consumers.hpp"

namespace hejmdal::radio::blocks {

TEST(TestConsumersBlocks, TestStateConsumer) {
  State prev_state = State::kNoData;
  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = std::make_shared<StateConsumer>(
      "", [&prev_state](const Meta&, const time::TimePoint&,
                        const State& state) { prev_state = state; });
  entry->OnStateOut(test);

  {
    entry->StateIn(Meta::kNull, time::Now(), State::kWarn);
    EXPECT_EQ(prev_state, State::kWarn);

    entry->StateIn(Meta::kNull, time::Now(), State::kOk);
    EXPECT_EQ(prev_state, State::kOk);

    entry->StateIn(Meta::kNull, time::Now(), State::kOk);
    EXPECT_EQ(prev_state, State::kOk);
  }
}

}  // namespace hejmdal::radio::blocks
