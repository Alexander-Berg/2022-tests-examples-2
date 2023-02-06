#include <enums/mask_serialization.hpp>

#include <gtest/gtest.h>

namespace tests {

enum Type { Undefined, Test0, Test1, Test2, kSize };
using Mask = enums::Mask<Type>;

void ToString(const Mask& mask) {
  const std::string str = enums::ToString(mask);
  EXPECT_EQ(str.size(), kSize);
  for (size_t i = 0; i < kSize; i++) {
    const Type value = static_cast<Type>(i);
    EXPECT_EQ(mask[value], str[kSize - 1 - i] - '0');
  }
}

void Parse(const std::string& str) {
  Mask mask = enums::Parse<Type>(str);
  const size_t m = std::min(static_cast<size_t>(kSize), str.size());
  size_t i;
  for (i = 0; i < m; i++) {
    const Type value = static_cast<Type>(i);
    EXPECT_EQ(mask[value], (str[m - 1 - i] == '1'));
  }
  for (; i < kSize; i++) {
    const Type value = static_cast<Type>(i);
    EXPECT_EQ(mask[value], false);
  }
}

}  // namespace tests

TEST(MaskSerialization, ToString) {
  tests::ToString({tests::Undefined});
  tests::ToString({tests::Test2});
  tests::ToString({tests::Undefined, tests::Test0, tests::Test1, tests::Test2});
  tests::ToString({tests::Undefined, tests::Test1});
  tests::ToString({tests::Test0, tests::Test2});
}

TEST(MaskSerialization, Parse) {
  tests::Parse("");
  tests::Parse("1");
  tests::Parse("0");
  tests::Parse("1111");
  tests::Parse("0000");
  tests::Parse("0101");
  tests::Parse("1010");

  EXPECT_THROW(enums::Parse<tests::Type>("abab"), std::invalid_argument);
}
