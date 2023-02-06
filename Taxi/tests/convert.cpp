#include <gtest/gtest.h>

#include "detail/convert.hpp"

using yson::detail::convert::impl::try_from_string;

TEST(convert, try_from_string_uint64_t_positive) {
    uint64_t result;

    EXPECT_TRUE(try_from_string(result, "0"));
    EXPECT_EQ(0ULL, result);

    EXPECT_TRUE(try_from_string(result, "100000"));
    EXPECT_EQ(100000ULL, result);

    EXPECT_TRUE(try_from_string(result, "9223372036854775807"));
    EXPECT_EQ(9223372036854775807ULL, result);

    EXPECT_TRUE(try_from_string(result, "18446744073709551615"));
    EXPECT_EQ(UINT64_MAX, result);
}

TEST(convert, try_from_string_uint64_t_negative) {
    uint64_t result;

    EXPECT_FALSE(try_from_string(result, ""));
    EXPECT_FALSE(try_from_string(result, "-"));
    EXPECT_FALSE(try_from_string(result, "-1"));
    EXPECT_FALSE(try_from_string(result, "foo"));
    EXPECT_FALSE(try_from_string(result, "100foo"));
    EXPECT_FALSE(try_from_string(result, "99999999999999999999999999999999"));
    EXPECT_FALSE(try_from_string(result, "18446744073709551616"));
}

TEST(convert, try_from_string_int64_t_positive) {
    int64_t result;

    EXPECT_TRUE(try_from_string(result, "0"));
    EXPECT_EQ(0LL, result);

    EXPECT_TRUE(try_from_string(result, "-0"));
    EXPECT_EQ(0LL, result);

    EXPECT_TRUE(try_from_string(result, "1"));
    EXPECT_EQ(1LL, result);

    EXPECT_TRUE(try_from_string(result, "-1"));
    EXPECT_EQ(-1LL, result);

    EXPECT_TRUE(try_from_string(result, "100000"));
    EXPECT_EQ(100000LL, result);

    EXPECT_TRUE(try_from_string(result, "-100000"));
    EXPECT_EQ(-100000LL, result);

    EXPECT_TRUE(try_from_string(result, "9223372036854775807"));
    EXPECT_EQ(INT64_MAX, result);

    EXPECT_TRUE(try_from_string(result, "-9223372036854775807"));
    EXPECT_EQ(-9223372036854775807LL, result);

    EXPECT_TRUE(try_from_string(result, "-9223372036854775808"));
    EXPECT_EQ(INT64_MIN, result);
}

TEST(convert, try_from_string_int64_t_negative) {
    int64_t result;

    EXPECT_FALSE(try_from_string(result, ""));
    EXPECT_FALSE(try_from_string(result, "-"));
    EXPECT_FALSE(try_from_string(result, "foo"));
    EXPECT_FALSE(try_from_string(result, "100foo"));
    EXPECT_FALSE(try_from_string(result, "99999999999999999999999999999999"));
    EXPECT_FALSE(try_from_string(result, "18446744073709551616"));
    EXPECT_FALSE(try_from_string(result, "18446744073709551615"));
    EXPECT_FALSE(try_from_string(result, "9223372036854775808"));
    EXPECT_FALSE(try_from_string(result, "-9223372036854775809"));
}

