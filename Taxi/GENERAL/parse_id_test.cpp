#include "parse_id.hpp"

#include <limits>
#include <optional>
#include <string>
#include <type_traits>

#include <gtest/gtest.h>

#include <userver/utils/strong_typedef.hpp>

using eats_catalog::utils::TryParseId;

TEST(TryParseId, Int64Valid) {
  static_assert(std::is_same_v<decltype(TryParseId<int64_t>("")),
                               std::optional<int64_t>>);

  ASSERT_EQ(TryParseId<int64_t>("0"), 0);
  ASSERT_EQ(TryParseId<int64_t>("1"), 1);
  ASSERT_EQ(TryParseId<int64_t>("2345"), 2345);

  ASSERT_EQ(TryParseId<int64_t>("999999999999999999"), 999999999999999999);
  ASSERT_EQ(TryParseId<int64_t>("9000000000000000000"), 9000000000000000000);
  static_assert(std::numeric_limits<int64_t>::max() == 9223372036854775807);
  ASSERT_EQ(TryParseId<int64_t>("9223372036854775807"), 9223372036854775807);
}

TEST(TryParseId, Int64Overflow) {
  static_assert(std::numeric_limits<int64_t>::max() == 9223372036854775807);
  ASSERT_EQ(TryParseId<int64_t>("9223372036854775808"), std::nullopt);
  ASSERT_EQ(TryParseId<int64_t>("9999999999999999999"), std::nullopt);
  ASSERT_EQ(TryParseId<int64_t>("10000000000000000000"), std::nullopt);
  ASSERT_EQ(TryParseId<int64_t>(std::string(1000, '5')), std::nullopt);
}

TEST(TryParseId, Invalid) {
  const auto invalid_strings = {"",    "01", "-1", "+1", "0x1",
                                "1.0", " 1", "1 ", "1s", "s"};

  for (const char* invalid_string : invalid_strings) {
    ASSERT_EQ(TryParseId<int64_t>(invalid_string), std::nullopt);
  }
}

TEST(TryParseId, StrongTypedef) {
  using Id = utils::StrongTypedef<class IdTag, int64_t>;

  static_assert(
      std::is_same_v<decltype(TryParseId<Id>("")), std::optional<Id>>);

  ASSERT_EQ(TryParseId<Id>("123"), Id{123});
  ASSERT_EQ(TryParseId<Id>("abc"), std::nullopt);
}
