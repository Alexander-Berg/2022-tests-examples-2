#include <gtest/gtest.h>

#include <utils/format_text.hpp>

std::string MakeStr(const int first, const int last) {
  std::string result;
  result.resize(static_cast<std::size_t>(std::max(0, last - first + 1)));

  for (std::size_t i = 0; i < result.size(); i++) {
    result[i] = static_cast<char>(first + i);
  }

  return result;
}

TEST(FormatText, All) {
  static const std::string kAbc = MakeStr(1, 127);

  using utils::FormatText;

  EXPECT_EQ("a!b{y}c", FormatText("a{x}b{y}c", {{"x", "!"}, {"z", "#"}}));
  EXPECT_EQ("123", FormatText("{a}{bc}", {{"a", "1"}, {"bc", "23"}}));
  EXPECT_EQ("", FormatText("{a}{bc}", {{"a", ""}, {"bc", ""}}));
  EXPECT_EQ("{a}b", FormatText("{a}b", {}));
  EXPECT_EQ(kAbc, FormatText("{key}", {{"key", kAbc}}));
  EXPECT_EQ(kAbc + "=" + kAbc, FormatText("{k}={k}", {{"k", kAbc}}));
}
