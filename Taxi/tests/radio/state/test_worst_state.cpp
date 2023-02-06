#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/state/worst_state.hpp"
#include "radio/blocks/utils/buffers.hpp"

namespace hejmdal::radio::blocks {

namespace {

time::TimePoint FromMillis(std::int64_t milliseconds_count) {
  return time::From<time::Milliseconds>(milliseconds_count);
}

}  // namespace

TEST(TestWorstStateBlocks, TestWorstStateWindow) {
  ::utils::datetime::MockNowSet(FromMillis(500));

  // deadline is 600ms, window duration is 100ms, so current window will be
  // [500ms, 600ms)
  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = std::make_shared<WorstStateWindow>(
      "", WorstStateWindowSettings{time::Milliseconds(100),
                                   time::Milliseconds(500), time::Minutes{10}});
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  {
    // let's ensure that last state is empty
    EXPECT_EQ(exit->LastTp(), FromMillis(0));
    EXPECT_EQ(exit->LastState(), State::kNoData);
  }

  {
    // no state change in window [500ms, 600ms)
    entry->StateIn(Meta::kNull, FromMillis(500), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(550), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(599), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(500));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    // state on 600ms triggers new window [600ms, 700ms)
    // Worst state of last window was kOk
    // kWarn if worst state of current window
    test->Tick(Meta::kNull, FromMillis(600));
    entry->StateIn(Meta::kNull, FromMillis(600), State::kWarn);
    EXPECT_EQ(exit->LastTp(), FromMillis(600));
    EXPECT_EQ(exit->LastState(), State::kWarn);
  }

  {
    // tick on 899ms changes window several times
    // we need to ensure, that we received kWarn from [600ms, 700ms)
    // and didnt' get anything from [700, 800)
    // notice: current window is [800, 900)
    test->Tick(Meta::kNull, FromMillis(899));
    EXPECT_EQ(exit->LastTp(), FromMillis(600));
    EXPECT_EQ(exit->LastState(), State::kWarn);
  }

  {
    // tick on 900ms changes window to [900, 1000)
    test->Tick(Meta::kNull, FromMillis(900));
    EXPECT_EQ(exit->LastTp(), FromMillis(600));
    EXPECT_EQ(exit->LastState(), State::kWarn);
  }

  {
    entry->StateIn(Meta::kNull, FromMillis(1000), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(1000))
        << std::chrono::duration_cast<time::Milliseconds>(
               exit->LastTp().time_since_epoch())
               .count();
    EXPECT_EQ(exit->LastState(), State::kWarn);
    entry->StateIn(Meta::kNull, FromMillis(1100), State::kOk);
    EXPECT_EQ(exit->LastTp(), FromMillis(1100));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    // State on 2000ms changes window several times
    // notice: current window is [2000, 2100)
    entry->StateIn(Meta::kNull, FromMillis(2000), State::kOk);

    EXPECT_EQ(exit->LastTp(), FromMillis(2000));
    EXPECT_EQ(exit->LastState(), State::kOk);

    entry->StateIn(Meta::kNull, FromMillis(2010), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(2020), State::kOk);

    // we don't send out repeating states in the same window
    EXPECT_EQ(exit->LastTp(), FromMillis(2000));
    EXPECT_EQ(exit->LastState(), State::kOk);

    entry->StateIn(Meta::kNull, FromMillis(2025), State::kCritical);

    // critical state is escalated, i. e. sent out immediately
    EXPECT_EQ(exit->LastTp(), FromMillis(2025));
    EXPECT_EQ(exit->LastState(), State::kCritical);

    entry->StateIn(Meta::kNull, FromMillis(2030), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(2040), State::kOk);
    entry->StateIn(Meta::kNull, FromMillis(2060), State::kWarn);
    entry->StateIn(Meta::kNull, FromMillis(2070), State::kOk);

    // Tick on 2100ms closes prev window with worst state kCritical
    test->Tick(Meta::kNull, FromMillis(2100));
    EXPECT_EQ(exit->LastTp(), FromMillis(2025));
    EXPECT_EQ(exit->LastState(), State::kCritical);
  }

  {
    // we go beyond no data offset
    test->Tick(Meta::kNull, FromMillis(2125) + time::Minutes{10});
    EXPECT_EQ(exit->LastTp(), FromMillis(2125));
    EXPECT_EQ(exit->LastState(), State::kNoData);
  }
}

UTEST(TestWorstStateBlocks, TestWorstState) {
  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = std::make_shared<WorstState>("");
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  auto meta = Meta::kNull;
  auto tp = time::Now();

  {
    EXPECT_EQ(test->Get(), std::nullopt);
    EXPECT_EQ(exit->LastState(), State::kNoData);

    entry->StateIn(meta, tp, State::kOk);
    EXPECT_EQ(test->Get()->state, State::kOk);
    EXPECT_EQ(exit->LastState(), State::kOk);

    entry->StateIn(meta, tp, State::kWarn);
    EXPECT_EQ(test->Get()->state, State::kWarn);
    EXPECT_EQ(exit->LastState(), State::kWarn);
    entry->StateIn(meta, tp, State::kOk);
    EXPECT_EQ(test->Get()->state, State::kWarn);
    EXPECT_EQ(exit->LastState(), State::kWarn);

    entry->StateIn(meta, tp, State::kError);
    EXPECT_EQ(test->Get()->state, State::kError);
    EXPECT_EQ(exit->LastState(), State::kError);
    entry->StateIn(meta, tp, State::kWarn);
    EXPECT_EQ(test->Get()->state, State::kError);
    EXPECT_EQ(exit->LastState(), State::kError);
    entry->StateIn(meta, tp, State::kOk);
    EXPECT_EQ(test->Get()->state, State::kError);
    EXPECT_EQ(exit->LastState(), State::kError);

    entry->StateIn(meta, tp, State::kCritical);
    EXPECT_EQ(test->Get()->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(meta, tp, State::kError);
    EXPECT_EQ(test->Get()->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(meta, tp, State::kWarn);
    EXPECT_EQ(test->Get()->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(meta, tp, State::kOk);
    EXPECT_EQ(test->Get()->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);

    auto last_value = test->GetAndReset(tp);
    EXPECT_EQ(test->Get(), std::nullopt);
    EXPECT_EQ(last_value->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(meta, tp, State::kOk);
    EXPECT_EQ(test->Get()->state, State::kOk);
    EXPECT_EQ(exit->LastState(), State::kOk);

    test->Reset(tp);
    EXPECT_EQ(test->Get(), std::nullopt);
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->StateIn(meta, tp, State::kCritical);
    EXPECT_EQ(test->Get()->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(meta, tp, State::kError);
    EXPECT_EQ(test->Get()->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(meta, tp, State::kWarn);
    EXPECT_EQ(test->Get()->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
    entry->StateIn(meta, tp, State::kOk);
    EXPECT_EQ(test->Get()->state, State::kCritical);
    EXPECT_EQ(exit->LastState(), State::kCritical);
  }
}

TEST(TestSerializeWorstStateWindow, SerializationTest) {
  ::utils::datetime::MockNowSet(FromMillis(500));
  auto original_minutes_window = WorstStateWindow(
      "some_name",
      {time::Minutes(100), time::Minutes(500), time::Minutes(1000)});
  auto original_minutes_window_json = original_minutes_window.Serialize();
  auto restored_minutes_window = WorstStateWindow(original_minutes_window_json);
  auto restored_minutes_window_json = restored_minutes_window.Serialize();
  EXPECT_EQ(original_minutes_window_json, restored_minutes_window_json);
  auto original_hours_window = WorstStateWindow(
      "another_name", {time::Hours(100), time::Hours(500), time::Hours(1000)});
  auto original_hours_window_json = original_hours_window.Serialize();
  auto restored_hours_window = WorstStateWindow(original_hours_window_json);
  auto restored_hours_window_json = restored_hours_window.Serialize();
  EXPECT_EQ(original_hours_window_json, restored_hours_window_json);
}

}  // namespace hejmdal::radio::blocks
