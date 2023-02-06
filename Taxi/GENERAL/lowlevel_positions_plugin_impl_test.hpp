#pragma once

#include <tuple>

namespace geobus::test {

inline void LowlevelPositionsTestPlugin::TestDriverPositionsAreClose(
    const lowlevel::DriverPositionInfo& first,
    const lowlevel::DriverPositionInfo& second,
    ComparisonPrecision requestedPrecision) {
  SCOPED_TRACE(__FUNCTION__);
  TestTrackPointsAreClose(first.point, second.point, requestedPrecision);
  EXPECT_EQ(first.driver_id, second.driver_id);
}

template <typename Iterator>
inline void LowlevelPositionsTestPlugin::TestDriverPositionsArrayAreEqual(
    Iterator start1, Iterator end1, Iterator start2, Iterator end2,
    ComparisonPrecision requestedPrecision) {
  SCOPED_TRACE(__FUNCTION__);
  using namespace ::testing;
  size_t iteration = 0;
  for (; start1 != end1 && start2 != end2; ++start1, ++start2, ++iteration) {
    SCOPED_TRACE(std::string("iterarion: ") + std::to_string(iteration));
    TestDriverPositionsAreClose(*start1, *start2, requestedPrecision);
  }

  EXPECT_EQ((start1 == end1), (start2 == end2));
}

}  // namespace geobus::test
