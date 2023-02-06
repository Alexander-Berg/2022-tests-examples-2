#include <gtest/gtest.h>

#include <psql/enum.hpp>

namespace {

enum class TestEnum { kElem1, kElem2, kElem3 };

}  // namespace

namespace psql {

template <>
struct EnumMapper<TestEnum> : EnumMapperBase<TestEnum> {
  EnumMapper()
      : EnumMapperBase<TestEnum>({{TestEnum::kElem1, "Elem1"},
                                  {TestEnum::kElem2, "Elem2"},
                                  {TestEnum::kElem3, "Elem3"}}) {}
};

}  // namespace psql

TEST(Enum, ToString) {
  EXPECT_EQ("Elem2",
            psql::EnumMapper<TestEnum>().by_value.at(TestEnum::kElem2));
}

TEST(Enum, FromString) {
  EXPECT_EQ(TestEnum::kElem2, psql::EnumMapper<TestEnum>().by_name.at("Elem2"));
}
