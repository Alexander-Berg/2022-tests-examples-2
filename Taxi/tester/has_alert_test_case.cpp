#include "has_alert_test_case.hpp"

#include <utils/json_field_check.hpp>

#include <fmt/format.h>

namespace hejmdal::radio::tester {

namespace params {
const std::string kMinAlertStateParamName = "min_alert_state";
}  // namespace params

void HasAlertTestCase::Initialize(formats::json::Value params) {
  if (auto alert_str = utils::JsonFieldCheck("HasAlertTestCase", params,
                                             params::kMinAlertStateParamName)
                           .String()
                           .GetOpt();
      alert_str.has_value()) {
    min_alert_state_ = State::FromString(std::move(alert_str.value()));
    if (min_alert_state_ < State::kWarn) {
      throw except::JsonFieldCheckFailed(
          "minimum alert state should be >= 'Warning' but '{}' is specified",
          min_alert_state_.ToString());
    }
  }
}

void HasAlertTestCase::StateInCallback(const time::TimePoint& tp,
                                       const State& state) {
  if (GetTimeRange().Contains(tp) && state >= min_alert_state_) {
    has_alert_ = true;
  }
}

TestCaseResult HasAlertTestCase::GetResult() const {
  TestCaseResult result(GetId(), GetType(), GetDescription());
  if (!has_alert_) {
    result.passed = false;
    result.error_message =
        fmt::format("Only states less than {} appeared in the given time range",
                    min_alert_state_.ToString());
  }
  return result;
}

}  // namespace hejmdal::radio::tester
