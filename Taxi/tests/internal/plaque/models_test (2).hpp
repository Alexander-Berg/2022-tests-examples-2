#pragma once

#include "internal/plaque.hpp"

namespace sweet_home::plaque {

std::unordered_map<std::string, Widget> PrepareWidgets();
std::unordered_map<std::string, Plaque> PreparePlaques(
    const std::unordered_map<std::string, Widget>& widgets);

}  // namespace sweet_home::plaque
