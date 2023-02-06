#include <gtest/gtest.h>

#include <helpers/cargo/cargo.hpp>

TEST(CheckRegex, SuccessErase) {
  auto result = helpers::cargo::ErasePickupCodeFromComment(
      "232 - код для получения заказа\nComment restaurant 1");

  ASSERT_EQ(result, "Comment restaurant 1");
}

TEST(CheckRegex, FailErase) {
  auto result =
      helpers::cargo::ErasePickupCodeFromComment("Comment restaurant 1");

  ASSERT_EQ(result, "Comment restaurant 1");
}
