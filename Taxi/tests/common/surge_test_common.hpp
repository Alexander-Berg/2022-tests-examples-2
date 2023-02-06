#pragma once

#include <iostream>

#include <surge/models/surge_map_index.hpp>

namespace surge {
namespace models {

bool operator==(const SurgeValue& lhs, const SurgeValue& rhs);

bool operator==(const SurgeTimings& lhs, const SurgeTimings& rhs);

template <typename TValue>
bool AreEuqal(
    const typename SurgeMapIndex<surge::models::HexValueGrid<TValue>>::Grid&
        lhs,
    const typename SurgeMapIndex<surge::models::HexValueGrid<TValue>>::Grid&
        rhs) {
  if (lhs.CellSizeMeter() != rhs.CellSizeMeter()) {
    return false;
  }

  const auto& lhs_envelope = lhs.Envelope();
  const auto& rhs_envelope = rhs.Envelope();

  if (lhs_envelope.max_corner() != rhs_envelope.max_corner()) {
    return false;
  }

  if (lhs_envelope.min_corner() != rhs_envelope.min_corner()) {
    return false;
  }

  if (lhs.BaseClass() != rhs.BaseClass()) {
    return false;
  }

  if (lhs.surge_map_values.size() != rhs.surge_map_values.size()) {
    return false;
  }

  for (const auto& category_values : lhs.surge_map_values) {
    const auto& category = category_values.first;
    const auto& values_lhs = category_values.second;
    auto values_rhs_it = rhs.surge_map_values.find(category);
    if (values_rhs_it == rhs.surge_map_values.end()) {
      return false;
    }

    const auto& values_rhs = values_rhs_it->second;

    if (values_lhs.size() != values_rhs.size()) {
      return false;
    }

    for (const auto& idx_value : values_lhs) {
      const auto& idx = idx_value.first;
      const auto& value_lhs = idx_value.second;
      auto value_rhs_it = values_rhs.find(idx);
      if (value_rhs_it == values_rhs.end()) {
        return false;
      }

      const auto& value_rhs = value_rhs_it->second;
      if (!(value_lhs == value_rhs)) return false;
    }
  }
  return true;
}

}  // namespace models
}  // namespace surge

namespace boost {
namespace geometry {
namespace model {

std::ostream& operator<<(std::ostream& os,
                         const surge::models::SurgeValueMapIndex::Box& box);

}  // namespace model
}  // namespace geometry
}  // namespace boost
