#pragma once

#include <optional>
#include <string>

#include <userver/formats/json/value.hpp>
#include <userver/storages/postgres/io/enum_types.hpp>

#include <models/declarations.hpp>
#include <radio/blocks/state.hpp>
#include <utils/time.hpp>

namespace hejmdal::models {

enum class TargetState { kOk, kWarn, kCrit };

struct TestData {
  std::int32_t id{-1};
  std::string description;
  models::CircuitSchemaId schema_id;
  time::TimePoint start_time;
  time::TimePoint precedent_time;
  time::TimePoint end_time;
  formats::json::Value data;
  formats::json::Value meta;
};

struct TestDataInfo {
  std::int32_t id;
  std::string description;
  models::CircuitSchemaId schema_id;
};

struct TestDataCreateResult {
  std::int32_t id;
};

}  // namespace hejmdal::models

namespace storages::postgres::io {

template <>
struct CppToUserPg<hejmdal::models::TargetState>
    : EnumMappingBase<hejmdal::models::TargetState> {
  static constexpr DBTypeName postgres_name = "public.target_state";
  static constexpr EnumeratorList enumerators{{EnumType::kOk, "OK"},
                                              {EnumType::kWarn, "WARN"},
                                              {EnumType::kCrit, "CRIT"}};
};

}  // namespace storages::postgres::io
