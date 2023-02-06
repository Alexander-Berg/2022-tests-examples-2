#pragma once

#include <endpoints/fallback/plugins/main_fallback/plugin.hpp>

namespace routestats::core {

using Decimal = decimal64::Decimal<4>;
using MinimalPrice = client_zone_geoindex::models::MinimalPrice;

MinimalPrice BuildDefaultMinimalPrice();

models::Country BuildDefaultCountry();

}  // namespace routestats::core
