#pragma once

#include <helpers/experiments3.hpp>
#include <userver/formats/json.hpp>

using MappedMockData = std::unordered_map<std::string, formats::json::Value>;

namespace zoneinfo {

Experiments3 MockExperiments3(const MappedMockData& mock_data);

}  // namespace zoneinfo
