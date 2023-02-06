#pragma once

#include <blocklist_client/models/blocklist_cache.hpp>
#include <userver/formats/json/serialize.hpp>

const auto kCarNumber = "car_number";
const auto kLicenseId = "license_id";
const auto kParkId = "park_id";
const auto kUuid = "uuid";
const auto kCarId = "car_id";

const std::string kNumber_1 = "number_1";
const std::string kNumber_2 = "number_2";
const std::string kNumber_3 = "number_3";

const std::string kPark_1 = "park_1";
const std::string kPark_2 = "park_2";

const std::string kLicense_1 = "license_1";
const std::string kLicense_2 = "license_2";

const std::string kCar_1 = "car_1";
const std::string kCar_2 = "car_2";

const std::string kUuid_1 = "uuid_1";
const std::string kUuid_2 = "uuid_2";

const std::string kEmptyPark = "";

static const auto kCarNumberPredicate = "11111111-1111-1111-1111-111111111111";
static const auto kParkIdAndCarNumberPredicate =
    "22222222-2222-2222-2222-222222222222";

static const formats::json::Value condition_1 =
    formats::json::FromString(R"=({"type":"eq","value":"car_number"})=");

static const formats::json::Value condition_2 = formats::json::FromString(
    R"=({"type":"and","value":[{"type":"eq","value":"park_id"},{"type":"eq","value":"car_number"}]})=");

static const predicate_evaluator::RawPredicatesMap raw_predicates_map = {
    {kCarNumberPredicate, condition_1},
    {kParkIdAndCarNumberPredicate, condition_2}};

predicate_evaluator::KwargsMap BuildKwargsMap(const std::string& car_number,
                                              const std::string& car_id,
                                              const std::string& park_id,
                                              const std::string& uuid,
                                              const std::string& license_id);

clients::blocklist::IndexableBlocksItem CreateItem(
    std::string id, std::vector<std::string> keys,
    std::vector<std::string> values, std::vector<bool> indexes,
    std::string predicate_id, bool is_active = true, std::string mechanics = {},
    std::string updated = {}, std::int64_t revision = {});
