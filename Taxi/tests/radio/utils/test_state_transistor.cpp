#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include <radio/blocks/commutation/entry_points.hpp>
#include <radio/blocks/state/state_transistor.hpp>
#include <radio/blocks/utils/buffers.hpp>

namespace hejmdal::radio::blocks {

const std::string block1_json = R"=(
{
  "type": "state_transistor",
  "id": "state_transistor_1",
  "lower": 0,
  "upper": 1,
  "default_state": "Ok"
}
)=";

TEST(TestSateTransistor, Test1) {
  auto entry_data = std::make_shared<DataEntryPoint>("entry_data");
  auto entry_state = std::make_shared<StateEntryPoint>("entry_state");
  auto block =
      std::make_shared<StateTransistor>(formats::json::FromString(block1_json));
  auto exit = std::make_shared<StateBuffer>("");
  entry_data->OnDataOut(block);
  entry_state->OnStateOut(block);
  block->OnStateOut(exit);

  entry_state->StateIn(Meta::kNull, time::Now(), State::kWarn);

  EXPECT_EQ(State::kOk, exit->LastState().GetStateValue());

  entry_data->DataIn(Meta::kNull, time::Now(), 0.5);
  entry_state->StateIn(Meta::kNull, time::Now(), State::kOk);

  EXPECT_EQ(State::kOk, exit->LastState().GetStateValue());

  entry_data->DataIn(Meta::kNull, time::Now(), 0.5);
  entry_state->StateIn(Meta::kNull, time::Now(), State::kWarn);

  EXPECT_EQ(State::kWarn, exit->LastState().GetStateValue());

  entry_data->DataIn(Meta::kNull, time::Now(), 1.5);
  entry_state->StateIn(Meta::kNull, time::Now(), State::kWarn);

  EXPECT_EQ(State::kOk, exit->LastState().GetStateValue());
}

const std::string block2_json = R"=(
{
  "type": "state_transistor",
  "id": "state_transistor_1",
  "lower": 0,
  "upper": 1
}
)=";

TEST(TestSateTransistor, Test2) {
  auto entry_data = std::make_shared<DataEntryPoint>("entry_data");
  auto entry_state = std::make_shared<StateEntryPoint>("entry_state");
  auto block =
      std::make_shared<StateTransistor>(formats::json::FromString(block2_json));
  auto exit = std::make_shared<StateBuffer>("");
  entry_data->OnDataOut(block);
  entry_state->OnStateOut(block);
  block->OnStateOut(exit);

  entry_data->DataIn(Meta::kNull, time::Now(), 0.5);
  entry_state->StateIn(Meta::kNull, time::Now(), State::kWarn);

  EXPECT_EQ(State::kWarn, exit->LastState().GetStateValue());

  entry_data->DataIn(Meta::kNull, time::Now(), 1.5);
  entry_state->StateIn(Meta::kNull, time::Now(), State::kOk);

  EXPECT_EQ(State::kWarn, exit->LastState().GetStateValue());
}
}  // namespace hejmdal::radio::blocks
