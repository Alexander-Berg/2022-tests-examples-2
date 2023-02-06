#pragma once

#include <cctz/time_zone.h>
#include <fmt/format.h>

#include <models/money.hpp>

namespace cart_delivery_fee::tests {

const cctz::time_zone kTimezone = cctz::utc_time_zone();

struct CartFeePair {
  models::Money subtotal{};
  models::Money delivery_fee{};

  inline std::string GetName() const {
    auto str = fmt::format("{}_{}", subtotal, delivery_fee);
    std::replace(str.begin(), str.end(), '.', '_');
    return str;
  }
};

struct CartFeeSurge {
  models::Money subtotal{};
  models::Money delivery_fee{};
  models::Money surge_part{};

  inline std::string GetName() const {
    auto str = fmt::format("{}_{}_{}", subtotal, delivery_fee, surge_part);
    std::replace(str.begin(), str.end(), '.', '_');
    return str;
  }
};

std::ostream& operator<<(std::ostream& os, const CartFeePair& pair);
std::ostream& operator<<(std::ostream& os, const CartFeeSurge& pair);

}  // namespace cart_delivery_fee::tests
