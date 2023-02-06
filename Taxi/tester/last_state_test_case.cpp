#include "last_state_test_case.hpp"

#include <utils/json_field_check.hpp>

#include <fmt/format.h>

namespace hejmdal::radio::tester {

namespace params {
const std::string kLastStateParamName = "last_state";
}  // namespace params

void LastStateTestCase::Initialize(formats::json::Value params) {
  expected_last_state_ =
      State::FromString(utils::JsonFieldCheck("LastStateTestCase", params,
                                              params::kLastStateParamName)
                            .Required()
                            .String()
                            .Get());
}

void LastStateTestCase::StateInCallback(const time::TimePoint& tp,
                                        const State& state) {
  if (GetTimeRange().Contains(tp)) {
    actual_last_state_ = state;
  }
}

TestCaseResult LastStateTestCase::GetResult() const {
  TestCaseResult result(GetId(), GetType(), GetDescription());
  if (!actual_last_state_.has_value()) {
    result.passed = false;
    result.error_message =
        "No any state values were received in given time range";
  } else if (actual_last_state_ != expected_last_state_) {
    result.passed = false;
    result.error_message = fmt::format(
        "Last known state is {} but {} is expected",
        actual_last_state_->ToString(), expected_last_state_.ToString());
  }
  return result;
}

}  // namespace hejmdal::radio::tester
