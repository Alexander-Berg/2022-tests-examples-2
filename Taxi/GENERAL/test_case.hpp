#pragma once

#include <boost/pfr/core.hpp>

#include <userver/formats/json/value.hpp>

#include <utils/time.hpp>

#include <src/defs/all_definitions.hpp>

namespace hejmdal::models::postgres {

struct TestCase {
  std::int32_t id{-1};
  std::string description;
  std::int32_t test_data_id;
  std::string schema_id;
  std::string out_point_id;
  time::TimePoint start_time;
  time::TimePoint end_time;
  std::string check_type;
  formats::json::Value check_params;
  bool is_enabled;

  auto Introspect() { return boost::pfr::structure_tie(*this); }

  auto Introspect() const { return boost::pfr::structure_tie(*this); }

  bool operator==(const TestCase& other) const;

  bool operator!=(const TestCase& other) const { return !(*this == other); }
};

struct TestCaseInfo {
  std::int32_t id;
  std::string description;
  std::string schema_id;
  std::string check_type;
  bool is_enabled;
};

}  // namespace hejmdal::models::postgres
