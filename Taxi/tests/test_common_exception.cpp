#include <gtest/gtest.h>
#include <ml/common/exception.hpp>

void Require(bool condition) {
  ML_REQUIRE(condition, "require failed "
                            << "lol");
}

TEST(Exception, Failing) {
  ASSERT_NO_THROW(Require(true));
  ASSERT_ANY_THROW(Require(false));
}
