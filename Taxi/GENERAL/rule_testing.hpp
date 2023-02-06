#pragma once

#include <pricing-extended/defs/definitions/rules.hpp>

namespace models {

struct TestResult {
  std::optional<bool> last_result;
  std::optional<int64_t> last_result_rule_id;
  std::optional<std::vector<int>> last_visited_lines;
};

struct RuleTestWithResult : handlers::libraries::pricing_extended::RuleTest,
                            TestResult {};

}  // namespace models
