#pragma once

#include <endpoints/fallback/plugins/main_fallback/plugin.hpp>

namespace routestats::fallback::main {

using Decimal = decimal64::Decimal<4>;
using MinimalPrice = client_zone_geoindex::models::MinimalPrice;

core::Zone BuildDefaultZone();

}  // namespace routestats::fallback::main
