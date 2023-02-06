#pragma once

#include <cstdint>
#include <ostream>

#include <gtest/gtest.h>

#include <cctz/time_zone.h>
#include <fmt/format.h>

#include <userver/logging/level.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/datetime.hpp>

#include <common_handlers/schedule/types.hpp>
#include <subvention_matcher/types.hpp>

namespace dt = utils::datetime;

class BaseTest : public ::testing::Test {
 protected:
  void SetUp() override {
    if (std::getenv("SV_TEST_LOG")) {
      old_ = logging::SetDefaultLogger(
          logging::MakeStderrLogger("cerr", logging::Level::kDebug));
    }
  }

  void TearDown() override {
    if (old_) {
      logging::SetDefaultLogger(std::move(old_));
    }
  }

 private:
  logging::LoggerPtr old_;
};

template <typename T>
class BaseTestWithParam : public ::testing::TestWithParam<T> {
 protected:
  void SetUp() override {
    if (std::getenv("SV_TEST_LOG")) {
      old_ = logging::SetDefaultLogger(
          logging::MakeStderrLogger("cerr", logging::Level::kDebug));
    }
  }

  void TearDown() override {
    if (old_) {
      logging::SetDefaultLogger(std::move(old_));
    }
  }

 private:
  logging::LoggerPtr old_;
};

inline subvention_matcher::Rule CreateRule(std::string&& zone,
                                           std::optional<std::string>&& geoarea,
                                           std::string&& tariff_class,
                                           int activity) {
  static uint32_t kId{0};
  subvention_matcher::Rule result;

  result.id = std::to_string(++kId);
  result.zone = std::move(zone);
  result.geoarea = std::move(geoarea);
  result.tariff_class = std::move(tariff_class);
  result.activity_points = activity;

  return result;
}

inline subvention_matcher::Rule CreateRuleWithId(
    std::string&& zone, std::optional<std::string>&& geoarea,
    std::string&& tariff_class, int activity, uint32_t id) {
  subvention_matcher::Rule result;

  result.id = std::to_string(id);
  result.zone = std::move(zone);
  result.geoarea = std::move(geoarea);
  result.tariff_class = std::move(tariff_class);
  result.activity_points = activity;

  return result;
}

inline subvention_matcher::Rule CreateExpandedRule(
    std::string zone, std::optional<std::string> geoarea,
    std::string tariff_class, int activity, uint32_t id, std::string draft_id) {
  subvention_matcher::Rule result;

  result.id = std::to_string(id);
  result.draft_id = draft_id;
  result.schedule_ref = draft_id;
  result.zone = std::move(zone);
  result.geoarea = std::move(geoarea);
  result.tariff_class = std::move(tariff_class);
  result.activity_points = activity;

  return result;
}

inline cctz::time_zone GetMskTz() {
  cctz::time_zone tz;
  cctz::load_time_zone("Europe/Moscow", &tz);
  return tz;
}

namespace std::chrono {

inline std::ostream& operator<<(std::ostream& os,
                                const system_clock::time_point& point) {
  return os << utils::datetime::Timestring(point);
}

}  // namespace std::chrono

namespace clients::billing_subventions_x {

inline std::ostream& operator<<(std::ostream& os, const SingleRideRule& rule) {
  return os << rule.id;
}

}  // namespace clients::billing_subventions_x

namespace handlers {

inline bool operator==(const ScheduleDay& lhs, const ScheduleDay& rhs) {
  return std::tie(lhs.day, lhs.from, lhs.to) ==
         std::tie(rhs.day, rhs.from, rhs.to);
}

inline std::ostream& operator<<(std::ostream& os,
                                const common_handlers::StepInfo& step) {
  return os << fmt::format("{}", step.bonus_amount);
}

}  // namespace handlers

namespace subvention_matcher {

inline std::ostream& operator<<(std::ostream& os, const Property& property) {
  return os << ToString(GetDriverPropertyType(property));
}

}  // namespace subvention_matcher
