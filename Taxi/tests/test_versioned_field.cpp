#include <chrono>

#include <gtest/gtest.h>

#include <views/versioned_field.hpp>

std::chrono::system_clock::time_point MockTime(std::time_t value) {
  return std::chrono::system_clock::from_time_t(value);
}

namespace parks_replica::views {

TEST(ParksReplica, Intersects) {
  {
    bool actual =
        Intersects(MockTime(1), MockTime(2), MockTime(3), MockTime(5));
    EXPECT_FALSE(actual);
  }
  {
    bool actual =
        Intersects(MockTime(2), MockTime(4), MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual =
        Intersects(MockTime(3), MockTime(4), MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual =
        Intersects(MockTime(3), MockTime(4), MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual =
        Intersects(MockTime(3), MockTime(4), MockTime(2), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual =
        Intersects(MockTime(4), MockTime(5), MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual =
        Intersects(MockTime(4), MockTime(6), MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual =
        Intersects(MockTime(5), MockTime(6), MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual =
        Intersects(MockTime(6), MockTime(7), MockTime(3), MockTime(5));
    EXPECT_FALSE(actual);
  }
  {
    bool actual = Intersects(MockTime(6), MockTime(7), {}, MockTime(5));
    EXPECT_FALSE(actual);
  }
  {
    bool actual = Intersects({}, {}, MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual = Intersects({}, {}, {}, {});
    EXPECT_TRUE(actual);
  }
  {
    bool actual = Intersects({}, MockTime(6), MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual = Intersects(MockTime(5), {}, MockTime(3), MockTime(5));
    EXPECT_TRUE(actual);
  }
  {
    bool actual = Intersects(MockTime(5), {}, MockTime(3), {});
    EXPECT_TRUE(actual);
  }
  {
    bool actual = Intersects(MockTime(3), {}, MockTime(5), {});
    EXPECT_TRUE(actual);
  }
  {
    bool actual = Intersects({}, MockTime(4), MockTime(3), {});
    EXPECT_TRUE(actual);
  }
  {
    bool actual = Intersects({}, MockTime(2), MockTime(3), {});
    EXPECT_FALSE(actual);
  }
}

}  // namespace parks_replica::views
