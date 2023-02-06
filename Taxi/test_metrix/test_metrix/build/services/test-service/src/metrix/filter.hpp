#pragma once

#include <taxi_config/variables/METRIX_AGGREGATION.hpp>

namespace metrix {
std::optional<std::string> GetFilteredLabel(
    const std::string& name, const std::string& value,
    const std::vector<taxi_config::metrix_aggregation::AggRule>& rules);
}
