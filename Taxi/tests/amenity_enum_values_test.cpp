#include <userver/utest/utest.hpp>
#include <userver/utils/underlying_value.hpp>

#include <defs/all_definitions.hpp>

TEST(Amenity, SerializationReliability) {
  EXPECT_EQ(utils::UnderlyingValue(handlers::Amenity::kConditioner), 0);
  EXPECT_EQ(utils::UnderlyingValue(handlers::Amenity::kWaitInDestination), 25);
}
