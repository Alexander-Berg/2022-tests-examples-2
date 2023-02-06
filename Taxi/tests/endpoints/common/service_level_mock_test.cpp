#include "service_level_mock_test.hpp"

namespace routestats::test {
namespace {
core::ServiceLevel GetDefaultServiceLevel(const std::string& class_name) {
  core::ServiceLevel result;
  result.class_ = class_name;
  result.eta = core::EstimatedWaiting{60, "1 min"};
  result.final_price = core::Decimal{100};
  result.is_fixed_price = true;
  return result;
}
}  // namespace

void ApplyExtensions(core::ServiceLevelExtensionsMap results,
                     std::vector<core::ServiceLevel>& levels) {
  for (auto& level : levels) {
    if (!results.count(level.Class())) continue;
    results.at(level.Class())->Apply("test", level);
  }
}

core::ServiceLevel MockDefaultServiceLevel(
    const std::string& class_name, std::optional<Configurator> handler) {
  auto result = GetDefaultServiceLevel(class_name);
  if (!handler) return result;

  auto func = *handler;
  if (func) func(result);
  return result;
}

}  // namespace routestats::test
