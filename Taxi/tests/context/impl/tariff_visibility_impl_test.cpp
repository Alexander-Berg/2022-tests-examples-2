#include <userver/utest/utest.hpp>

#include <core/context/tariff_visibility/tariff_visibility_impl.hpp>

namespace routestats::core {

std::vector<std::string> OrderCategories(
    const std::vector<std::string>& allowed,
    const std::vector<std::string>& ordered);

std::vector<std::string> GetAllowedCategories(
    const std::vector<std::string>& categories,
    const std::unordered_map<std::string, VisibilityAttributes>& visibility);

TEST(OrderCategories, HappyPath) {
  const auto allowed = std::vector<std::string>{"uber3", "uber5", "uber1",
                                                "uber9", "uber7", "uber10"};
  const auto ordered =
      std::vector<std::string>{"uber1", "uber2", "uber3", "uber4"};
  const auto expected = std::vector<std::string>{"uber1", "uber3", "uber5",
                                                 "uber9", "uber7", "uber10"};
  const auto result = OrderCategories(allowed, ordered);
  ASSERT_EQ(result, expected);
}

TEST(GetAllowedCategories, HappyPath) {
  const auto categories =
      std::vector<std::string>{"econom", "vip", "supervip", "takoe", "ultima"};
  const auto visibility = std::unordered_map<std::string, VisibilityAttributes>{
      {"econom", {false, false}},
      {"takoe", {true, false}},
      {"vip", {false, true}},
      {"supervip", {true, true}}};

  const auto result = GetAllowedCategories(categories, visibility);
  const auto expected = std::vector<std::string>{"econom", "takoe"};
  ASSERT_EQ(result, expected);
}

}  // namespace routestats::core
