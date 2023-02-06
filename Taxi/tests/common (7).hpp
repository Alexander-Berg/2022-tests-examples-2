#pragma once

#include <ostream>

#include <gtest/gtest.h>

#include <cctz/time_zone.h>
#include <fmt/format.h>

#include <userver/logging/level.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/datetime.hpp>

#include <subvention_matcher/impl/impl.hpp>
#include <subvention_matcher/types.hpp>
#include "defs/api/api.hpp"

namespace dt = utils::datetime;

class BaseTest : public ::testing::Test {
 protected:
  void SetUp() override {
    if (std::getenv("SV_TEST_LOG")) {
      old_ = logging::SetDefaultLogger(
          logging::MakeStderrLogger("cerr", logging::Level::kDebug));
      logging::SetDefaultLoggerLevel(logging::Level::kTrace);
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

namespace subvention_matcher {

inline std::ostream& operator<<(std::ostream& os, const Property& property) {
  return os << ToString(GetDriverPropertyType(property));
}

}  // namespace subvention_matcher

namespace handlers {

inline std::ostream& operator<<(std::ostream& os, const TimeRange& range) {
  return os << "from: " << range.from << "; to: " << range.to;
}

}  // namespace handlers
