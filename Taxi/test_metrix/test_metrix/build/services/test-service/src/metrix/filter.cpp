#include <metrix/filter.hpp>

#include <userver/utils/overloaded.hpp>

namespace metrix {
std::optional<std::string> GetFilteredLabel(
    const std::string& name, const std::string& value,
    const std::vector<taxi_config::metrix_aggregation::AggRule>& rules) {
  bool label_found = false;
  for (const auto& rule : rules) {
    auto ret = std::visit(
        utils::Overloaded{
            [&label_found, &name, &value](
                const taxi_config::metrix_aggregation::Whitelist& whitelist)
                -> std::optional<std::string> {
              if (whitelist.label_name == name) {
                label_found = true;
                if (std::find(whitelist.values.begin(), whitelist.values.end(),
                              value) != whitelist.values.end()) {
                  return value;
                } else if (whitelist.use_others) {
                  return "others";
                }
              }
              return std::nullopt;
            },
            [&label_found, &name,
             &value](const taxi_config::metrix_aggregation::Grouping& grouping)
                -> std::optional<std::string> {
              if (grouping.label_name == name) {
                label_found = true;
                for (const auto& group : grouping.groups) {
                  if (std::find(group.values.begin(), group.values.end(),
                                value) != group.values.end()) {
                    return group.group_name;
                  }
                }
                if (grouping.use_others) {
                  return "others";
                }
              }
              return std::nullopt;
            }}, rule.AsVariant());
    if (label_found) {
      return ret;
    }
  }
  return value;
}
}  // namespace metrix
