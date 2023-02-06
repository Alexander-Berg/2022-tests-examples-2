#pragma once
#include <userver/formats/json.hpp>

namespace eats_restapp_menu::merging {
using JsonVal = formats::json::Value;

bool CheckJsonEquals(const JsonVal& first, const JsonVal& second);
}  // namespace eats_restapp_menu::merging
