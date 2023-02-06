#pragma once

#include <gtest/gtest.h>

#include <geometry/position.hpp>
#include <geometry/units.hpp>

#include <gpssignal/gps_signal.hpp>
#include <gpssignal/units.hpp>

#include <boost/units/io.hpp>
#include <optional>

namespace gpssignal {

template <typename T>
inline void PrintToOptionalUnit(const std::optional<T>& value,
                                std::ostream* os) {
  if (value) {
    *os << value->value();
  } else {
    *os << "none";
  }
}

inline void PrintTo(const GpsSignal& gps_signal, std::ostream* os) {
  *os << "[lat, lon]: " << gps_signal.latitude.value() << ","
      << gps_signal.longitude.value();
  *os << " [dir, spd, acc]: ";
  PrintToOptionalUnit(gps_signal.direction, os);
  *os << ", ";
  PrintToOptionalUnit(gps_signal.speed, os);
  *os << ", ";
  PrintToOptionalUnit(gps_signal.accuracy, os);
  *os << " timestamp: "
      << std::chrono::system_clock::to_time_t(gps_signal.timestamp);
}

}  // namespace gpssignal
