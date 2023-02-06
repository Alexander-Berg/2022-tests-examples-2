#include <gtest/gtest.h>

#include <memory>

#include <testing/source_path.hpp>
#include <userver/utest/utest.hpp>

#include "utils/time.hpp"

#include <radio/blocks/state/worst_state.hpp>
#include "radio/blocks/commutation/output_consumer.hpp"
#include "radio/circuit.hpp"

namespace hejmdal::radio {

struct StateTime {
  blocks::State state;
  time::TimePoint time;
};

class StateCollector : public blocks::Block {
 public:
  StateCollector() : Block("test-state-collector"), states_() {}

  const std::string& GetType() const override { return type_; }
  virtual formats::json::Value Serialize() const override {
    return formats::json::Value();
  }

  void StateIn(const blocks::Meta&, const time::TimePoint& time,
               const blocks::State& state) override {
    states_.push_back(StateTime{state, time});
  }

  std::vector<StateTime> Extract() {
    auto tmp = std::move(states_);
    states_.clear();
    return tmp;
  }

 private:
  std::vector<StateTime> states_;
  static const std::string type_;
};
const std::string StateCollector::type_ = "test-state-collector";

class StateOut : public blocks::OutputConsumer {
 public:
  StateOut()
      : OutputConsumer("test-state-out"),
        wsw_("", {time::Minutes{1}, time::Minutes{5}, time::Minutes{10}}),
        collector_() {
    wsw_.OnStateOut(&collector_);
  }
  const std::string& GetType() const override { return type_; }
  virtual formats::json::Value Serialize() const override {
    return formats::json::Value();
  }

  void StateIn(const blocks::Meta& meta, const time::TimePoint& time,
               const blocks::State& state) override {
    wsw_.StateIn(meta, time, state);
  }

  std::vector<StateTime> Extract() { return collector_.Extract(); }

 private:
  blocks::WorstStateWindow wsw_;
  StateCollector collector_;
  static const std::string type_;
};
const std::string StateOut::type_ = "test-state-out";

void CheckCircuit(std::shared_ptr<Circuit>& circuit_ptr) {
  auto now = time::Now();
  auto t = [&now](int millis) { return now + time::Milliseconds{millis}; };
  auto& circuit = *circuit_ptr;
  auto out = std::make_shared<StateOut>();
  auto ep = circuit.GetEntryPoint("data");
  circuit.GetOutPoint("state").OnStateOut(out);

  circuit.Tick(t(10000));

  ep.DataIn(t(10000), 10.);
  {
    auto states = out->Extract();

    ASSERT_EQ(states.size(), 1u);
    // Ok state is escalated by WorstStateWindow immediately
    EXPECT_EQ(states[0].state, blocks::State::kOk);
    ASSERT_EQ(out->Extract().size(), 0u);
  }
  ep.DataIn(t(10100), 10.1);
  circuit.Tick(t(20000));
  ep.DataIn(t(20200), 10.2);
  ep.DataIn(t(20300), 10.);
  circuit.Tick(t(30000));
  ep.DataIn(t(30400), 10.1);
  circuit.Tick(t(40000));
  ep.DataIn(t(40500), 10.2);
  circuit.Tick(t(50000));
  ep.DataIn(t(50600), 10.);
  circuit.Tick(t(60000));
  ep.DataIn(t(60700), 10.1);
  circuit.Tick(t(70000));
  ep.DataIn(t(70800), 10.2);
  circuit.Tick(t(80000));
  ep.DataIn(t(80900), 10.);
  circuit.Tick(t(90000));

  {
    auto states = out->Extract();

    ASSERT_EQ(states.size(), 1u);
    EXPECT_EQ(states[0].state, blocks::State::kOk);
    ASSERT_EQ(out->Extract().size(), 0u);
  }

  ep.DataIn(t(100000), 10.);
  ep.DataIn(t(118000), 120);  // <-- out of bounds value
  {
    auto states = out->Extract();

    ASSERT_EQ(states.size(), 1u);
    EXPECT_EQ(states[0].state, blocks::State(blocks::State::kWarn));
    ASSERT_EQ(out->Extract().size(), 0u);
  }
  ep.DataIn(t(129000), 10.2);
  ep.DataIn(t(137000), 10.);
  ep.DataIn(t(144000), 10.1);
  ep.DataIn(t(152000), 10.2);
  ep.DataIn(t(163000), 10.);
  ep.DataIn(t(174000), 10.1);

  circuit.Tick(t(200000));

  circuit.Tick(t(280000));
  circuit.Tick(t(380000));
  circuit.Tick(t(480000));
  circuit.Tick(t(580000));

  { ASSERT_EQ(out->Extract().size(), 0u); }
}

TEST(TestStatBlocks, TestCircuitFromJSON) {
  formats::json::Value sigma_schema = formats::json::blocking::FromFile(
      utils::CurrentSourcePath("src/radio/circuits/circuit_sigma.json"));
  auto circuit_ptr = Circuit::Build("test-circuit", sigma_schema);
  CheckCircuit(circuit_ptr);
}

}  // namespace hejmdal::radio
