#pragma once

#include "internal/plaque/models.hpp"

namespace plus_plaque::plaque {

std::unordered_map<std::string, Widget> PrepareWidgets();
std::unordered_map<std::string, WidgetsLevel> PrepareLevels(
    const std::unordered_map<std::string, Widget>& widgets);
std::unordered_map<std::string, Plaque> PreparePlaques(
    const std::unordered_map<std::string, WidgetsLevel>& widgets_levels);

}  // namespace plus_plaque::plaque
