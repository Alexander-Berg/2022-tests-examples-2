#include <common/utils/common.hpp>

#include <userver/utest/utest.hpp>

namespace bsx_common = billing_subventions_x::utils::common;

enum class TestEnumClass { a, b };

std::string ToString(TestEnumClass val) {
  switch (val) {
    case TestEnumClass::a:
      return "a";
    case TestEnumClass::b:
      return "b";
  }
}

using StrictString = ::utils::StrongTypedef<class StrictStringTag, std::string>;

using StrictInt = ::utils::StrongTypedef<class StrictIntTag, int>;

TEST(CommonUtilsTest, GetUnderlying_test) {
  const std::optional<StrictString> opt_string = StrictString("123");
  EXPECT_EQ(bsx_common::GetUnderlying(opt_string), opt_string->GetUnderlying());
  const std::optional<StrictString> null_string;
  EXPECT_EQ(bsx_common::GetUnderlying(null_string), std::nullopt);
  const std::optional<StrictInt> opt_int = StrictInt(100500);
  EXPECT_EQ(bsx_common::GetUnderlying(opt_int), opt_int->GetUnderlying());
}

TEST(CommonUtilsTest, Transform_test) {
  const std::vector<int> v1 = {1, 2};
  const std::vector<std::string> expected = {"1", "2"};
  const auto to_string_func = [](auto val) { return std::to_string(val); };
  EXPECT_EQ(bsx_common::Transform(v1, to_string_func), expected);
}
