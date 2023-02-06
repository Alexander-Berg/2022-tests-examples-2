#include <gtest/gtest.h>

#include <testing/source_path.hpp>

#include <radio/circuit.hpp>

#include "../tools/testutils.hpp"

namespace hejmdal::radio {

static void TestKsSchema(CircuitPtr circuit) {
  auto json_test_data = formats::json::blocking::FromFile(
      testutils::kStasticDir + "/ks_test_inputs/ks_block_test.json");
  auto data = testutils::LoadJsonTS(json_test_data["data"]);
  auto p_values = testutils::LoadJsonTS(json_test_data["ks"]);

  auto consumer = std::make_shared<testutils::TestOutputConsumer>();
  circuit->GetOutPoint("alert").OnStateOut(consumer);

  auto entry = circuit->GetEntryPoint("entry_data");

  auto states = consumer->buffer.ExtractState();
  EXPECT_EQ(states.size(), 0);

  for (const auto& sample : data) {
    circuit->Tick(sample.GetTime());
    entry.DataIn(sample.GetTime(), sample.GetValue());
  }

  states = consumer->buffer.ExtractState();

  EXPECT_EQ(p_values.size(), states.size());

  for (size_t i = 0; i < states.size(); ++i) {
    auto p_value_sample = p_values.at(i);
    auto state_sample = states.at(i);
    EXPECT_EQ(p_value_sample.GetTime(), state_sample.GetTime());
    bool is_ok = p_value_sample.GetValue() >= 1e-8;
    auto state_value = state_sample.GetValue().GetStateValue();
    if (is_ok) {
      EXPECT_EQ(blocks::State::kOk, state_value);
    } else {
      EXPECT_EQ(blocks::State::kWarn, state_value);
    }
  }
}

TEST(TestCircuitKs, TestJsonBuild) {
  auto schema = formats::json::blocking::FromFile(
      ::utils::CurrentSourcePath("src/radio/circuits/circuit_ks.json"));

  auto circuit = Circuit::Build("ks", schema);
  EXPECT_TRUE(circuit != nullptr);

  TestKsSchema(circuit);
}

}  // namespace hejmdal::radio
