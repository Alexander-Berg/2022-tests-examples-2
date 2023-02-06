#pragma once

#include <radio/tester/test_case_base.hpp>

namespace hejmdal::radio::tester {

inline const std::string kWorstStateTestCaseType = "worst_state";

class WorstStateTestCase final : public TestCaseBase {
 public:
  using TestCaseBase::TestCaseBase;

  const std::string& GetType() const override {
    return kWorstStateTestCaseType;
  };

  void Initialize(formats::json::Value params) override;
  TestCaseResult GetResult() const override;
  void StateInCallback(const time::TimePoint& tp, const State& state) override;

 private:
  State worst_state_;
  bool should_reach_worst_state_;
  bool worst_state_reached_ = false;
  std::optional<std::pair<time::TimePoint, State>> first_error_ = std::nullopt;
};

}  // namespace hejmdal::radio::tester
