#include <gtest/gtest.h>

#include <views/cars/car_create_or_modify.hpp>

TEST(CorrectSetObjectFields, All) {
  using views::cars::internal::CorrectSetObjectFields;

  const auto& old =
      BSON("ca" << BSON("a" << true << "b" << false << "c" << true) << "am"
                << BSON("1" << false << "2" << true) << "other"
                << "xxx"
                << "other_old" << 0);
  const auto& set =
      BSON("ca.a" << false << "ca.b" << false << "ca.d" << false << "ca.e"
                  << true << "am.2" << false << "other" << 432 << "other_set"
                  << "yyy");
  const auto& result =
      BSON("other" << 432 << "other_set"
                   << "yyy"
                   << "am" << BSON("2" << false << "1" << false) << "ca"
                   << BSON("a" << false << "b" << false << "d" << false << "e"
                               << true << "c" << true));

  EXPECT_EQ(old, (CorrectSetObjectFields(old, set, {"am", "ca"}, {})));
  EXPECT_EQ(set, (CorrectSetObjectFields(set, old, {"abra"}, {})));
  EXPECT_EQ(result, (CorrectSetObjectFields(set, old, {"am", "ca"}, {})));

  const auto& bad_set = BSON("ca.a" << 0);
  EXPECT_EQ(bad_set, (CorrectSetObjectFields(bad_set, old, {"ca"}, {})));
}
