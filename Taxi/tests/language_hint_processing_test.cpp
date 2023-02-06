#include <gtest/gtest.h>
#include <unordered_set>

#include "models/chat.hpp"

namespace chat {
namespace components {
namespace internal {
std::vector<std::string> ProcessHint(
    const chat::models::LanguageHint& hint,
    const std::unordered_set<std::string>& supported);
}  // namespace internal
}  // namespace components
}  // namespace chat

TEST(ProcessHint, Basic) {
  const std::unordered_set<std::string> supported_langs = {"ru", "en", "de",
                                                           "zh"};
  auto f = chat::components::internal::ProcessHint;
  using P = std::vector<std::string>;
  using H = chat::models::LanguageHint;

  EXPECT_EQ(P({"ru", "en", "zh"}),
            f(H{{"ru_RU", "en_US", "et-EE"}, "zh-CN", {}}, supported_langs));

  EXPECT_EQ(P{}, f(H{}, {}));
}
