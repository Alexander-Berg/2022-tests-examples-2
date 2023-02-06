#pragma once

#include <radio/tester/test_case_base.hpp>

namespace hejmdal::radio::tester {

inline const std::string kLastStateTestCaseType = "last_state";

class LastStateTestCase final : public TestCaseBase {
 public:
  using TestCaseBase::TestCaseBase;

  const std::string& GetType() const override {
    return kLastStateTestCaseType;
  };

  void Initialize(formats::json::Value params) override;
  TestCaseResult GetResult() const override;
  void StateInCallback(const time::TimePoint& tp, const State& state) override;

 private:
  State expected_last_state_;
  std::optional<State> actual_last_state_ = std::nullopt;
};

}  // namespace hejmdal::radio::tester
