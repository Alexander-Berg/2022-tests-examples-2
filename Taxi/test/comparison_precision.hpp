#pragma once

namespace geobus::test {

/// Some adjustment are required if conversion to and from flatbuffers
/// was preformed
enum class ComparisonPrecision {
  /// Data was converted to and from flatbuffers. Because fbs have limited
  /// precision for some variables, they will be compared with higher
  /// threshold
  /// E.g. speed is in m/s and in double in our codebase, but in kmph and
  /// in short in fbs.
  FbsPrecision,
  /// Use standard threshold when comparing values.
  FullPrecision
};
static constexpr const double kFbsSpeedMpsPrecision = 1.0;
static constexpr const double kFbsSpeedKmphPrecision = 1.0;
static constexpr const double kSpeedKmphPrecision = 0.1;

}  // namespace geobus::test
