#include "encoded_polyline.hpp"

#include <gtest/gtest.h>

TEST(DecodePolyline, Base) {
  using ::geometry::lat;
  using ::geometry::lon;
  const auto ret =
      internal::polyline::DecodePolyline("_p~iF~ps|U_ulLnnqC_mqNvxq`@");
  const auto expected = std::vector<::geometry::Position>{
      {38.5 * lat, -120.2 * lon},
      {40.7 * lat, -120.95 * lon},
      {43.252 * lat, -126.453 * lon},
  };
  ASSERT_EQ(expected, ret);
}
