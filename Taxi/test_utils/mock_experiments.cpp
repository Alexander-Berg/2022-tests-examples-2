#include "mock_experiments.hpp"

namespace zoneinfo {

Experiments3 MockExperiments3(const MappedMockData& mock_data) {
  ExpMappedData exp3_data;
  for (const auto& [name, value] : mock_data) {
    exp3_data[name] = {name, value, {}};
  }
  return {exp3_data};
}  // namespace zoneinfo

}  // namespace zoneinfo
