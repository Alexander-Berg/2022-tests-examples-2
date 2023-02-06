#include <gtest/gtest.h>

#include <userver/formats/json/value_builder.hpp>
#include <utils/except.hpp>

#include <radio/blocks/math/quartile_bounds.hpp>
#include "radio/blocks/commutation/entry_points.hpp"
#include "radio/blocks/state/out_of_bounds_state.hpp"
#include "radio/blocks/utils/buffers.hpp"

namespace hejmdal::radio::blocks {

namespace {

time::TimePoint FromMillis(std::int64_t milliseconds_count) {
  return time::From<time::Milliseconds>(milliseconds_count);
}

}  // namespace

TEST(TestOobBlocks, TestOutOfBoundsState) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto entry_bounds = std::make_shared<BoundsEntryPoint>("");
  auto test = std::make_shared<OutOfBoundsState>("");
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnDataOut(test);
  entry_bounds->OnBoundsOut(test);
  test->OnStateOut(exit);

  auto meta = Meta::kNull;
  auto tp = time::Now();

  {
    // buffer is empty
    EXPECT_EQ(exit->LastTp(), FromMillis(0));
    EXPECT_EQ(exit->LastState(), State::kNoData);
  }

  {
    // sending some data, no bounds yet
    entry->DataIn(meta, tp, 10.0);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->DataIn(meta, tp, -10.0);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->DataIn(meta, tp, -10000.0);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->DataIn(meta, tp, 1000000.0);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->DataIn(meta, tp, 0.0);
    EXPECT_EQ(exit->LastTp(), tp);
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    // adding bounds
    entry_bounds->BoundsIn(meta, FromMillis(1), -10.0, 10.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(1));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    entry->DataIn(meta, FromMillis(3), 10.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(3));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->DataIn(meta, FromMillis(4), -10.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(4));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->DataIn(meta, FromMillis(5), 5.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(5));
    EXPECT_EQ(exit->LastState(), State::kOk);
    entry->DataIn(meta, FromMillis(6), -5.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(6));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    // sending out of bounds value that changes state
    entry->DataIn(meta, FromMillis(10), 100.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(10));
    EXPECT_EQ(exit->LastState(), State::kWarn);
  }

  {
    // new out of bounds values update state
    entry->DataIn(meta, FromMillis(15), 100.0);
    entry->DataIn(meta, FromMillis(15), -100.0);
    entry->DataIn(meta, FromMillis(15), -1000.0);
    entry->DataIn(meta, FromMillis(15), 100000.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(15));
    EXPECT_EQ(exit->LastState(), State::kWarn);
  }

  {
    // returning to in-bounds data
    entry->DataIn(meta, FromMillis(20), 10.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(20));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    // new values with-in bounds change state
    entry->DataIn(meta, tp, 10.0);
    entry->DataIn(meta, tp, -10.0);
    entry->DataIn(meta, tp, 5.0);
    entry->DataIn(meta, FromMillis(25), -5.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(25));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }

  {
    // new bounds that don't contain prev data
    entry_bounds->BoundsIn(meta, FromMillis(30), -1.0, 1.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(30));
    EXPECT_EQ(exit->LastState(), State::kWarn);
  }

  {
    // new out of bounds values update state
    entry->DataIn(meta, FromMillis(35), 100.0);
    entry->DataIn(meta, FromMillis(35), -100.0);
    entry->DataIn(meta, FromMillis(35), -1000.0);
    entry->DataIn(meta, FromMillis(35), 100000.0);
    EXPECT_EQ(exit->LastTp(), FromMillis(35));
    EXPECT_EQ(exit->LastState(), State::kWarn);
  }

  {
    // new bounds that contain prev data
    entry_bounds->BoundsIn(meta, FromMillis(50), 10000, 1000000);
    EXPECT_EQ(exit->LastTp(), FromMillis(50));
    EXPECT_EQ(exit->LastState(), State::kOk);
  }
}

template <class T>
std::string OptToString(const std::optional<T>& value) {
  if (value) return std::to_string(*value);
  return "(nullopt)";
}

void TestOverride(
    std::optional<double> fixed_lower_bound,
    std::optional<double> fixed_upper_bound,
    const std::pair<double, double>& in_bounds,
    const std::vector<std::pair<double, State::Value>>& expected_response) {
  formats::json::ValueBuilder builder;
  builder["id"] = "test_oob";
  builder["type"] = "out_of_bounds_state";
  if (fixed_lower_bound) builder["fixed_lower_bound"] = *fixed_lower_bound;
  if (fixed_upper_bound) builder["fixed_upper_bound"] = *fixed_upper_bound;

  auto entry = std::make_shared<DataEntryPoint>("");
  auto entry_bounds = std::make_shared<BoundsEntryPoint>("");
  auto test = std::make_shared<OutOfBoundsState>(builder.ExtractValue());
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnDataOut(test);
  entry_bounds->OnBoundsOut(test);
  test->OnStateOut(exit);

  auto meta = Meta::kNull;
  size_t current_time = 1;

  entry_bounds->BoundsIn(meta, FromMillis(current_time), in_bounds.first,
                         in_bounds.second);

  for (const auto& [in_value, expected_out_state] : expected_response) {
    ++current_time;
    entry->DataIn(meta, FromMillis(current_time), in_value);
    EXPECT_EQ(expected_out_state, exit->LastState().GetStateValue())
        << "time: " << current_time << ", in value: " << in_value
        << ", in bounds: " << in_bounds.first << ", " << in_bounds.second
        << ", fixed bounds: " << OptToString(fixed_lower_bound) << ", "
        << OptToString(fixed_upper_bound);
  }
}

TEST(TestOobBlocks, TestOutOfBoundsStateOverride) {
  TestOverride(std::nullopt, std::nullopt, {-10, 10},
               {{-5, State::kOk},
                {5, State::kOk},
                {-15, State::kWarn},
                {15, State::kWarn}});

  TestOverride(-6, std::nullopt, {-10, 10},
               {{-5, State::kOk},
                {5, State::kOk},
                {-15, State::kWarn},
                {15, State::kWarn}});
  TestOverride(-4, std::nullopt, {-10, 10},
               {{-5, State::kWarn},
                {5, State::kOk},
                {-15, State::kWarn},
                {15, State::kWarn}});
  TestOverride(-16, std::nullopt, {-10, 10},
               {{-5, State::kOk},
                {5, State::kOk},
                {-15, State::kOk},
                {15, State::kWarn}});

  TestOverride(std::nullopt, 6, {-10, 10},
               {{-5, State::kOk},
                {5, State::kOk},
                {-15, State::kWarn},
                {15, State::kWarn}});
  TestOverride(std::nullopt, 4, {-10, 10},
               {{-5, State::kOk},
                {5, State::kWarn},
                {-15, State::kWarn},
                {15, State::kWarn}});
  TestOverride(std::nullopt, 16, {-10, 10},
               {{-5, State::kOk},
                {5, State::kOk},
                {-15, State::kWarn},
                {15, State::kOk}});
}

namespace {

struct Env {
  std::shared_ptr<DataEntryPoint> entry;
  std::shared_ptr<BoundsEntryPoint> entry_bounds;
  std::shared_ptr<OutOfBoundsState> test;
  std::shared_ptr<StateBuffer> exit;
};

Env CreateEnv(const std::optional<std::string>& alert_text_template = {}) {
  formats::json::ValueBuilder builder;
  builder["id"] = "oob_test";
  builder["type"] = "out_of_bounds_state";
  if (alert_text_template.has_value()) {
    builder["alert_text_template"] = alert_text_template.value();
  }
  builder["yield_state_on_bounds_in"] = false;

  auto entry = std::make_shared<DataEntryPoint>("");
  auto entry_bounds = std::make_shared<BoundsEntryPoint>("");
  auto test = std::make_shared<OutOfBoundsState>(builder.ExtractValue());
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnDataOut(test);
  entry_bounds->OnBoundsOut(test);
  test->OnStateOut(exit);
  return {entry, entry_bounds, test, exit};
}

}  // namespace

TEST(TestOobBlocks, TestDescriptionTemplate) {
  auto [entry, entry_bounds, test, exit] = CreateEnv(std::string(
      "circuit_id: {circuit_id}, value: {value:.1f}, value_percent : "
      "{value_percent:.0f}%, bound: {bound:.1f}, {{word_in_brackets}}"));

  auto meta = Meta::kNull;
  size_t current_time = 1;

  entry_bounds->BoundsIn(Meta::kNull, FromMillis(current_time), 0.0, 1.0);

  {
    entry->DataIn(Meta::kNull, FromMillis(++current_time), -1.0);
    EXPECT_EQ(State::kWarn, exit->LastState().GetStateValue());
    std::string expected =
        "circuit_id: (no circuit), value: -1.0, value_percent : -100%, bound: "
        "0.0, {word_in_brackets}";
    std::string description = exit->LastState().GetDescription();
    EXPECT_EQ(expected, description);
  }

  {
    entry->DataIn(Meta::kNull, FromMillis(++current_time), 2.0);
    EXPECT_EQ(State::kWarn, exit->LastState().GetStateValue());
    std::string expected =
        "circuit_id: (no circuit), value: 2.0, value_percent : 200%, bound: "
        "1.0, {word_in_brackets}";
    std::string description = exit->LastState().GetDescription();
    EXPECT_EQ(expected, description);
  }
}

TEST(TestOobBlocks, TestInvalidDescriptionTemplate) {
  {
    EXPECT_ANY_THROW(CreateEnv(std::string(
        "circuit_id: {circuit_id}, value: {value:.1f, value_percent : "
        "{value_percent:.0f}%, bound: {bound:.1f}")));
  }
  {
    EXPECT_ANY_THROW(CreateEnv(
        std::string("circuit_id: {circuit_id}, value: {}, value_percent : "
                    "{value_percent:.0f}%, bound: {bound:.1f}")));
  }
  { EXPECT_ANY_THROW(CreateEnv(std::string("circuit_id: {"))); }
}

TEST(TestOobBlocks, TestDefaultDescriptionTemplate) {
  auto [entry, entry_bounds, test, exit] = CreateEnv();

  auto meta = Meta::kNull;
  size_t current_time = 1;

  entry_bounds->BoundsIn(Meta::kNull, FromMillis(current_time), 0.0, 1.0);

  {
    entry->DataIn(Meta::kNull, FromMillis(++current_time), -1.0);
    EXPECT_EQ(State::kWarn, exit->LastState().GetStateValue());
    std::string expected =
        "(no circuit), limit has been reached: current value = -1.000";
    std::string description = exit->LastState().GetDescription();
    EXPECT_EQ(expected, description);
  }
}

TEST(TestOobBlock, TestBlockParams) {
  auto entry = std::make_shared<DataEntryPoint>("");
  auto idq = std::make_shared<IDQBoundsGeneratorSample>("idq", 10, 1);

  auto oob_params = formats::json::MakeObject(
      "id", "oob", "type", "out_of_bounds_state", "yield_state_on_bounds_in",
      false, "alert_text_template",
      "median: {block_params__idq__median:.1f}, value: {value:.1f}, "
      "circuit_id: {circuit_id}");

  auto oob = std::make_shared<OutOfBoundsState>(oob_params);
  auto exit = std::make_shared<StateBuffer>("");
  entry->OnDataOut(oob);
  entry->OnDataOut(idq);
  idq->OnBoundsOut(oob);
  oob->OnStateOut(exit);

  auto meta = Meta::kNull;
  size_t current_time = 1;

  for (; current_time < 11; ++current_time) {
    entry->DataIn(meta, FromMillis(current_time), 1.2345);
  }

  EXPECT_EQ(State::kOk, exit->LastState().GetStateValue());

  ++current_time;
  entry->DataIn(meta, FromMillis(current_time), 10.0);

  EXPECT_EQ(State::kWarn, exit->LastState().GetStateValue());

  std::string expected_description(
      "median: 1.2, value: 10.0, circuit_id: (no circuit)");
  EXPECT_EQ(expected_description, exit->LastState().GetDescription());
}

}  // namespace hejmdal::radio::blocks
