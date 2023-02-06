#include <gtest/gtest.h>

#include <memory>

#include <userver/formats/json/value_builder.hpp>

#include "radio/blocks/block.hpp"
#include "radio/blocks/block_factory.hpp"
#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/meta.hpp"
#include "radio/blocks/other/schmitt_state_window.hpp"
#include "radio/blocks/utils/buffers.hpp"
#include "utils/time.hpp"

namespace hejmdal::radio::blocks {
TEST(TestSchmittStateWindowBlocks, TestSchmittStateWindow) {
  formats::json::ValueBuilder builder;
  builder["type"] = "schmitt_state_window";
  builder["id"] = "test";
  builder["upper_time_ms"] = 3000;
  builder["lower_time_ms"] = 2000;

  auto entry = std::make_shared<StateEntryPoint>("");
  auto test = BlockFactory::CreateBlock(builder.ExtractValue());
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnStateOut(test);
  test->OnStateOut(exit);

  auto current_time = time::From<time::Milliseconds>(1000);
  auto sec_step = time::Seconds{1};
  auto small_step = time::Milliseconds{100};

  {
    EXPECT_EQ(exit->LastTp(), time::TimePoint{});
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kNoData);
  }

  {
    entry->StateIn(Meta::kNull, current_time, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kNoData);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kNoData);

    entry->StateIn(Meta::kNull, current_time += small_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kNoData);

    entry->StateIn(Meta::kNull, current_time += small_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kNoData);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kNoData);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
  }

  {
    entry->StateIn(Meta::kNull, current_time += sec_step, State::kWarn);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);

    entry->StateIn(Meta::kNull, current_time += small_step, State::kWarn);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kCritical);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kCritical);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kCritical);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kWarn);

    entry->StateIn(Meta::kNull, current_time += small_step, State::kCritical);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kWarn);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kCritical);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kCritical);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kCritical);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kCritical);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);
  }

  {
    entry->StateIn(Meta::kNull, current_time += sec_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);

    entry->StateIn(Meta::kNull, current_time += small_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);

    entry->StateIn(Meta::kNull, current_time += small_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kCritical);

    entry->StateIn(Meta::kNull, current_time += sec_step, State::kOk);
    EXPECT_EQ(exit->LastTp(), current_time);
    EXPECT_EQ(exit->LastState().GetStateValue(), State::kOk);
  }
}
}  // namespace hejmdal::radio::blocks
