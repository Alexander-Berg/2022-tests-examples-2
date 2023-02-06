#include <gtest/gtest.h>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/state/no_data_state.hpp"
#include "radio/blocks/utils/buffers.hpp"

namespace hejmdal::radio::blocks {

TEST(TestDataStateBlocks, TestDataState) {
  auto now = time::Now();
  auto entry = std::make_shared<DataEntryPoint>("");
  auto test = std::make_shared<NoDataState>(
      "", time::Seconds{120}, time::Seconds{300}, "hello {no_data_duration}",
      State::kWarn, true, true);
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  {
    // start state
    entry->NoDataIn(Meta::kNull, now);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kWarn);

    // data in
    entry->DataIn(Meta::kNull, now, 0);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
    EXPECT_EQ(exit->LastTp(), now);

    // ok check
    entry->NoDataIn(Meta::kNull, now + time::Minutes{1});
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
    EXPECT_EQ(exit->LastTp(), now + time::Minutes{1});

    // warn check
    entry->NoDataIn(Meta::kNull, now + time::Minutes{3});
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kWarn);
    EXPECT_EQ(exit->LastState().GetDescription(), "hello 3m");
    EXPECT_EQ(exit->LastTp(), now + time::Minutes{3});

    // crit check
    entry->NoDataIn(Meta::kNull, now + time::Minutes{6});
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);
    EXPECT_EQ(exit->LastState().GetDescription(), "hello 6m");
    EXPECT_EQ(exit->LastTp(), now + time::Minutes{6});

    // data in
    entry->DataIn(Meta::kNull, now + time::Minutes{7}, 0);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
    EXPECT_EQ(exit->LastTp(), now + time::Minutes{7});

    // ok check
    entry->NoDataIn(Meta::kNull, now + time::Minutes{8});
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
    EXPECT_EQ(exit->LastTp(), now + time::Minutes{8});
  }
}

TEST(TestDataStateBlocks, TestSerialize) {
  auto serialization = formats::json::MakeObject(
      "id", "hello", "no_data_duration_before_warn_sec", 60);

  auto now = time::Now();
  auto entry = std::make_shared<DataEntryPoint>("");
  auto test = std::make_shared<NoDataState>(serialization);
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  // data in
  entry->DataIn(Meta::kNull, now, 0);
  EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
  EXPECT_EQ(exit->LastTp(), now);

  // ok check
  entry->NoDataIn(Meta::kNull, now + time::Seconds{30});
  EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
  EXPECT_EQ(exit->LastTp(), now + time::Seconds{30});

  // warn check
  entry->NoDataIn(Meta::kNull, now + time::Minutes{2});
  EXPECT_EQ(exit->LastState().GetStateValue(), State::kWarn);
  EXPECT_EQ(exit->LastTp(), now + time::Minutes{2});
}

TEST(TestDataStateBlocks, TestDontYieldStateOnData) {
  auto serialization = formats::json::MakeObject(
      "id", "hello", "no_data_duration_before_warn_sec", 60,
      "yield_data_present_state", false);

  auto now = time::Now();
  auto entry = std::make_shared<DataEntryPoint>("");
  auto test = std::make_shared<NoDataState>(serialization);
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  // no state on data
  entry->DataIn(Meta::kNull, now, 0);
  EXPECT_EQ(exit->LastTp(), time::TimePoint{});

  // ok check
  entry->NoDataIn(Meta::kNull, now + time::Seconds{30});
  EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
  EXPECT_EQ(exit->LastTp(), now + time::Seconds{30});

  // no state on data
  entry->DataIn(Meta::kNull, now + time::Minutes{2}, 1);
  EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
  EXPECT_EQ(exit->LastTp(), now + time::Seconds{30});

  // warn check
  entry->NoDataIn(Meta::kNull, now + time::Minutes{4});
  EXPECT_EQ(exit->LastState().GetStateValue(), State::kWarn);
  EXPECT_EQ(exit->LastTp(), now + time::Minutes{4});
}

}  // namespace hejmdal::radio::blocks
