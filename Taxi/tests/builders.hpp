#pragma once

#include <userver/utest/utest.hpp>

#include <string>
#include <utility>

#include "smart_rules/types/base_types.hpp"
#include "smart_rules/types/goal/rule.hpp"

using Goal = billing_subventions_x::types::GoalRule;
using TimePoint = billing_subventions_x::types::TimePoint;

TimePoint ATimePoint(const std::string& value);
std::string TimePointsNotEqual(TimePoint actual, TimePoint expected);

class GoalBuilder {
 public:
  GoalBuilder& WithStartsAt(std::string value) {
    start_ = std::move(value);
    return *this;
  }

  GoalBuilder WithWindow(int value) {
    window_ = value;
    return *this;
  }

  Goal Build() const {
    Goal goal;
    goal.starts_at = ATimePoint(start_);
    goal.window_size = window_;
    return goal;
  }

 private:
  std::string start_;
  int window_;
};
