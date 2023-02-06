#include <gtest/gtest.h>

#include <utils/flags.hpp>

enum class FooFlags : int {
  Foo = 1,
  Bar = 2,
  Maurice = 4,
};
DECLARE_FLAGS(FooFlags)

TEST(utils_flags, flags_bits) {
  utils::Flags<FooFlags> flags = FooFlags::Foo | FooFlags::Bar;
  auto flags2 = flags | FooFlags::Maurice;
  EXPECT_TRUE(flags & FooFlags::Foo);
  EXPECT_TRUE(flags & FooFlags::Bar);
  EXPECT_FALSE(flags & FooFlags::Maurice);
  EXPECT_TRUE(flags2 & FooFlags::Maurice);
}
