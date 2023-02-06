#include <gtest/gtest.h>

#include <userver/formats/json.hpp>

#include <testing/source_path.hpp>

#include <radio/blocks/utils/sample_buffers.hpp>
#include <radio/circuit.hpp>
#include "../tools/testutils.hpp"

namespace hejmdal::radio {

static time::Seconds sec = time::Seconds(1);

static void TestSchema(CircuitPtr circuit) {
  EXPECT_EQ(circuit->GetRequiredHistoryDataDuration(), time::Seconds{900});

  auto now = time::Now();
  auto consumer = std::make_shared<testutils::TestOutputConsumer>();
  circuit->GetOutPoint("alert").OnStateOut(consumer);

  auto limit = circuit->GetEntryPoint("limit");
  auto usage = circuit->GetEntryPoint("usage");

  limit.DataIn(now, 4.);
  auto states = consumer->buffer.ExtractState();
  EXPECT_EQ(states.size(), 0);

  for (int i = 0; i < 600; i += 5) {
    usage.DataIn(now + i * sec, 2.);
  }

  states = consumer->buffer.ExtractState();
  EXPECT_EQ(states.size(), 120);

  for (const auto& s : states) {
    EXPECT_EQ(s.GetValue(), blocks::State::kOk);
  }

  usage.DataIn(now + 601 * sec, 2.);
  usage.DataIn(now + 1950 * sec, 5.);
  usage.DataIn(now + 2200 * sec, 10.);
  states = consumer->buffer.ExtractState();
  EXPECT_EQ(states.size(), 3);
  EXPECT_EQ(states[0].GetValue(), blocks::State::kOk);
  EXPECT_EQ(states[1].GetValue(), blocks::State::kOk);
  EXPECT_EQ(states[2].GetValue(), blocks::State::kWarn);
}

TEST(TestCircuitRtcResourceUsage, TestJsonBuild) {
  auto schema = formats::json::blocking::FromFile(::utils::CurrentSourcePath(
      "src/radio/circuits/circuit_rtc_resource_usage.json"));

  auto circuit = Circuit::Build("test_rtc_resource_usage", schema);
  EXPECT_TRUE(circuit != nullptr);

  TestSchema(circuit);
}

}  // namespace hejmdal::radio
