#pragma once

#include <string>
#include <unordered_map>
#include <unordered_set>
#include <variant>

#include <utils/types.hpp>

constexpr auto kDefault = "__default__";
const auto kValidInfinity = utils::TimePoint::max();
const auto kValidLimited =
    utils::datetime::Stringtime("2018-07-09T13:56:07.000+0000");
const std::unordered_set<std::string> kTags{"benua", "developer", "yandex"};
const std::unordered_map<std::string, models::TagInfo> kTagsInfo{
    {"benua", {kValidInfinity, {}}},
    {"developer", {kValidLimited, {}}},
    {"yandex", {kValidInfinity, {}}}};

using PriorityRule = handlers::PriorityRule;
