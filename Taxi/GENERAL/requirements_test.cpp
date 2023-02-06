#include "requirements.hpp"

#include <gtest/gtest.h>
#include <boost/version.hpp>

//#if BOOST_VERSION >= 105800
//#define VARIANT_EXPECT_NE(expected, actual) EXPECT_NE(expected, actual)
//#else  // BOOST_VERSION >= 105800
// do not has operator !=
#define VARIANT_EXPECT_NE(expected, actual) EXPECT_FALSE(expected == actual)
//#endif  // BOOST_VERSION >= 105800

TEST(Requirements, Bool) {
  const models::requirements::Value bool_value(true);

  EXPECT_TRUE(models::requirements::Value(true) == bool_value);
  EXPECT_TRUE(models::requirements::Description::True == bool_value);

  // const char* -> bool :(
  // int -> bool :(

  using number_t = models::requirements::number_t;
  VARIANT_EXPECT_NE(models::requirements::Value(false), bool_value);
  VARIANT_EXPECT_NE(models::requirements::Description::False, bool_value);
  VARIANT_EXPECT_NE(models::requirements::Value(number_t(0)), bool_value);
  VARIANT_EXPECT_NE(models::requirements::Value(std::string()), bool_value);
  VARIANT_EXPECT_NE(models::requirements::Value(number_t(1)), bool_value);
  VARIANT_EXPECT_NE(models::requirements::Value(std::string("1")), bool_value);
}
