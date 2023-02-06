#pragma once

#include <geometry/position.hpp>
#include <geometry/viewport.hpp>

#include <geometry/test/geometry_generator.hpp>

namespace gpssignal::test {

/// This plugin provides functions for creating and comparing gps signals  and
/// related classes.
/// Passing same salt will result in same value
/// All double/float members are created with integer values to allow comparison
/// with '=='
class GpsSignalGenerator : public ::geometry::test::GeometryGenerator {
 public:
  static ::gpssignal::Speed CreateSpeed(const size_t salt) {
    return ::gpssignal::Speed::from_value(10 + (salt % 30) + 0.25);
  }

  static ::geometry::Distance CreateAccuracy(const size_t salt) {
    return (salt % 30) * ::geometry::meter;
  }

  /// Calling with same argument will provide same result
  static ::gpssignal::GpsSignal CreateGpsSignal(const size_t salt) {
    ::gpssignal::GpsSignal ret{CreateLatitude(salt), CreateLongitude(salt)};
    ret.speed = CreateSpeed(salt);
    ret.accuracy = CreateAccuracy(salt);
    ret.direction = CreateDirection(salt);
    ret.timestamp =
        std::chrono::system_clock::from_time_t(1563287792 + salt % 10000);

    return ret;
  }
};

}  // namespace gpssignal::test
