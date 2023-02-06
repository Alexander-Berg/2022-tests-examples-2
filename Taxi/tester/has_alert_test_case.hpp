#pragma once

#include <radio/tester/test_case_base.hpp>

namespace hejmdal::radio::tester {

inline const std::string kHasAlertTestCaseType = "has_alert";

class HasAlertTestCase final : public TestCaseBase {
 public:
  using TestCaseBase::TestCaseBase;

  const std::string& GetType() const override { return kHasAlertTestCaseType; };

  void Initialize(formats::json::Value params) override;
  TestCaseResult GetResult() const override;
  void StateInCallback(const time::TimePoint& tp, const State& state) override;

 private:
  State min_alert_state_ = State::kWarn;
  bool has_alert_ = false;
};

}  // namespace hejmdal::radio::tester
