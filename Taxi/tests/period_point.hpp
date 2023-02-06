#pragma once

#include <types/period_point.hpp>

namespace eats_report_storage::types {

inline static bool operator==(const PeriodPoint& lhs,
                              const PeriodPoint& rhs) noexcept {
  // clang-format off
  return std::tie(lhs.value, lhs.status, lhs.from, lhs.to,
                  lhs.xlabel, lhs.combined_count) ==
         std::tie(rhs.value, rhs.status, rhs.from, rhs.to,
                  rhs.xlabel, rhs.combined_count);
  // clang-format on
}

}  // namespace eats_report_storage::types
