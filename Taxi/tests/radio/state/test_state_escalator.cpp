#include <gtest/gtest.h>

#include <userver/formats/json/inline.hpp>

#include <radio/blocks/block_factory.hpp>
#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/utils/buffers.hpp>
#include <utils/except.hpp>
#include <utils/time.hpp>

namespace hejmdal::radio::blocks {

bool EqState(const State& s1, const State& s2) {
  return s1.GetStateValue() == s2.GetStateValue() &&
         s1.GetDescription() == s2.GetDescription();
}

TEST(TestBlocks, StateEscalator) {
  auto block_config = formats::json::MakeObject(
      "type", "state_escalator", "id", "test", "escalate_from", "Warning",
      "escalate_to", "Critical", "escalate_after_min", 60, "is_enabled", true);

  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = BlockFactory::CreateBlock(block_config);
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  auto meta = Meta::kNull;
  auto now = std::chrono::system_clock::from_time_t(10000);

  static const auto k1Mins = time::Minutes{1};
  static const auto k10Mins = time::Minutes{10};

  {
    // buffer is empty
    EXPECT_EQ(exit->LastTp(), time::TimePoint{});
    EXPECT_EQ(exit->LastState(), State::kNoData);
  }

  entry->StateIn(meta, now, State::kOk);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_EQ(exit->LastState(), State::kOk);

  entry->StateIn(meta, now += k10Mins, State::kOk);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_EQ(exit->LastState(), State::kOk);

  auto warn_state = State(State::kWarn, "test description");

  entry->StateIn(meta, now += k10Mins, warn_state);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_TRUE((EqState(exit->LastState(), warn_state)));

  entry->StateIn(meta, now += k10Mins, warn_state);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_TRUE((EqState(exit->LastState(), warn_state)));

  entry->StateIn(meta, now += k10Mins, State::kOk);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_EQ(exit->LastState(), State::kOk);

  entry->StateIn(meta, now += k10Mins, warn_state);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_TRUE((EqState(exit->LastState(), warn_state)));

  entry->StateIn(meta, now += 6 * k10Mins, warn_state);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_TRUE((EqState(exit->LastState(), warn_state)));

  auto expected_crit_state = State(State::kCritical, "test description");

  entry->StateIn(meta, now += k1Mins, warn_state);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_TRUE((EqState(exit->LastState(), expected_crit_state)));

  entry->StateIn(meta, now += k1Mins, warn_state);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_TRUE((EqState(exit->LastState(), expected_crit_state)));

  entry->StateIn(meta, now += k10Mins, State::kOk);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_EQ(exit->LastState(), State::kOk);

  entry->StateIn(meta, now += k10Mins, warn_state);
  EXPECT_EQ(exit->LastTp(), now);
  EXPECT_TRUE((EqState(exit->LastState(), warn_state)));
}

}  // namespace hejmdal::radio::blocks
