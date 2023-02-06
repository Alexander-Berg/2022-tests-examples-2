#include <utils/concurrent_idx_dict.hpp>

#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

UTEST(ConcurrentIdxDict, Simple) {
  utils::ConcurrentIdxDict<> dict("test");
  EXPECT_EQ(0u, dict.GetKeysSize());
  EXPECT_ANY_THROW(dict.GetKey(0));
  EXPECT_ANY_THROW(dict.GetKey(1));
  EXPECT_ANY_THROW(dict.GetKey(1));

  for (const auto& key : {"one", "two", "three"}) dict.GetOrCreateIdx(key);
  EXPECT_EQ(3u, dict.GetKeysSize());
  EXPECT_EQ(3u, dict.GetKeys().size());

  EXPECT_TRUE(dict.FindIdx("two").has_value());
  EXPECT_FALSE(dict.FindIdx("four").has_value());

  auto four_idx = dict.GetOrCreateIdx("four");
  EXPECT_EQ(four_idx, dict.GetOrCreateIdx("four"));
  EXPECT_EQ(four_idx, dict.FindIdx("four").value_or(-1));
  EXPECT_EQ(std::string("four"), dict.GetKey(four_idx));

  EXPECT_EQ(4u, dict.GetKeysSize());
  EXPECT_EQ(4u, dict.GetKeys().size());

  EXPECT_ANY_THROW(dict.GetKey(-1));
}

UTEST(ConcurrentIdxDict, Validator) {
  utils::ConcurrentIdxDict<> dict("test", [](const std::string& key) {
    return !key.empty() && key.front() == '#';
  });
  EXPECT_EQ(0u, dict.GetKeysSize());

  for (const auto& key : {"#one", "#two", "#three"}) {
    EXPECT_NO_THROW(dict.GetOrCreateIdx(key));
  }
  EXPECT_EQ(3u, dict.GetKeysSize());

  for (const auto& key : {"four", "five", "six"}) {
    EXPECT_ANY_THROW(dict.GetOrCreateIdx(key));
  }
  EXPECT_EQ(3u, dict.GetKeysSize());
}
