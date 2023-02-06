#include <gtest/gtest.h>

#include <testing/source_path.hpp>

#include <radio/circuit.hpp>

#include "../tools/testutils.hpp"

namespace hejmdal::radio {

blocks::DebugBufferPtr FindDebugBuffer(
    const std::string& name,
    const std::vector<blocks::DebugBufferPtr>& buffers) {
  for (auto buffer : buffers) {
    //        std::cerr << buffer->GetId() << std::endl;
    if (buffer->GetId() == name) return buffer;
  }
  throw std::logic_error("could not find buffer with name " + name);
}

void TestIqrSchema(CircuitPtr circuit, double rps, bool always_ok) {
  static const time::Seconds kSec = time::Seconds(1);

  auto dbg_buffers = circuit->CreateDebugBuffers(100);

  auto consumer = std::make_shared<testutils::TestOutputConsumer>();

  circuit->GetOutPoint("alert").OnStateOut(consumer);
  auto entry = circuit->GetEntryPoint("entry_timings");
  auto entry_rps = circuit->GetEntryPoint("entry_rps");

  auto states = consumer->buffer.ExtractState();
  EXPECT_EQ(states.size(), 0);

  auto now = time::Now();
  for (int i = 1; i < 62; ++i) {
    entry.DataIn(now, double(i % 10));
    entry_rps.DataIn(now, rps);
    now += kSec;
    states = consumer->buffer.ExtractState();
    auto expected = i == 1 ? blocks::State::kNoData : blocks::State::kOk;
    EXPECT_EQ(expected, states.back().GetValue().GetStateValue())
        << "point number " << i;
  }
  // now the median should be 5, IQR should be 5 => bounds should be 30 and -20
  auto bounds_buf = FindDebugBuffer("iqr_bounds_bounds", dbg_buffers);
  auto bounds =
      std::dynamic_pointer_cast<blocks::BoundsBufferSample>(bounds_buf)
          ->ExtractBounds();
  ASSERT_LE(1u, bounds.size());

  EXPECT_DOUBLE_EQ(30.0, bounds.back().GetValue().upper);
  EXPECT_DOUBLE_EQ(-20.0, bounds.back().GetValue().lower);

  entry.DataIn(now, 40.0);
  now += kSec;

  // should be ok because of schmitt
  EXPECT_EQ(blocks::State::kOk,
            consumer->buffer.ExtractState().back().GetValue().GetStateValue());

  entry.DataIn(now, 40.0);
  now += kSec;

  // now should warn if not muted by low rps
  if (always_ok) {
    EXPECT_EQ(
        blocks::State::kOk,
        consumer->buffer.ExtractState().back().GetValue().GetStateValue());
  } else {
    EXPECT_EQ(
        blocks::State::kWarn,
        consumer->buffer.ExtractState().back().GetValue().GetStateValue());
  }

  entry.DataIn(now, 5.0);
  now += kSec;

  // now should be ok again
  EXPECT_EQ(blocks::State::kOk,
            consumer->buffer.ExtractState().back().GetValue().GetStateValue());
}

CircuitPtr CreateIqrCircuit() {
  auto schema = formats::json::blocking::FromFile(
      ::utils::CurrentSourcePath("src/radio/circuits/circuit_iqr.json"));

  auto circuit = Circuit::Build("iqr", schema);
  EXPECT_TRUE(circuit != nullptr);
  return circuit;
}

TEST(TestCircuitIqr, TestJsonBuild) {
  TestIqrSchema(CreateIqrCircuit(), 10, false);
}

TEST(TestCircuitIqr, TestJsonBuildLowRps) {
  TestIqrSchema(CreateIqrCircuit(), 4, true);
}

}  // namespace hejmdal::radio
