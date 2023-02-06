#pragma once
#include <userver/formats/json/serialize.hpp>
#include <userver/fs/blocking/read.hpp>

namespace grocery_discounts_calculator {

formats::json::Value ReadFile(const std::string& name);

}  // namespace grocery_discounts_calculator
