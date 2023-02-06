#include <gtest/gtest.h>

#include "utils/utils.hpp"

namespace ucommunications {

TEST(UtilsTest, CountArgs) {
  std::string empty_string{};
  std::string not_empty_string = "one";
  std::optional<std::string> empty_arg{};
  std::optional<std::string> not_empty_arg = std::string("one");

  EXPECT_EQ(0, utils::CountArgs());
  EXPECT_EQ(0, utils::CountArgs(empty_string));
  EXPECT_EQ(1, utils::CountArgs(not_empty_string));
  EXPECT_EQ(0, utils::CountArgs(empty_string, empty_string));
  EXPECT_EQ(1, utils::CountArgs(empty_string, not_empty_string));
  EXPECT_EQ(1, utils::CountArgs(not_empty_string, empty_string));
  EXPECT_EQ(2, utils::CountArgs(not_empty_string, not_empty_string));
  EXPECT_EQ(2,
            utils::CountArgs(not_empty_string, not_empty_string, empty_string));

  EXPECT_EQ(0, utils::CountArgs(empty_arg, empty_string));
  EXPECT_EQ(1, utils::CountArgs(not_empty_arg, empty_string, empty_arg));
  EXPECT_EQ(2, utils::CountArgs(not_empty_arg, empty_string, not_empty_string));
  EXPECT_EQ(3,
            utils::CountArgs(not_empty_arg, not_empty_arg, not_empty_string));
}

TEST(UtilsTest, MaskPhone) {
  EXPECT_EQ("...", utils::MaskPhone(""));
  EXPECT_EQ("...", utils::MaskPhone("+79"));
  EXPECT_EQ("...", utils::MaskPhone("+790"));
  EXPECT_EQ("+7...01", utils::MaskPhone("+7901"));
  EXPECT_EQ("+7...33", utils::MaskPhone("+79001112233"));
}

TEST(UtilsTest, MaskText) {
  const auto input = formats::json::FromString(R"(
    {
      "key": "key",
      "keyset": "keyset",
      "params": {
        "string_param": "String",
        "localized_param": {
          "key": "second_key",
          "keyset": "second_keyset",
          "params": {
            "some_param": "some_param"
          }
        },
        "array_param": ["string", "other_string"],
        "number": 1000,
        "null": null,
        "empty_string": "",
        "string_1_len": "s"
      }
    }
  )");
  const auto expected = formats::json::FromString(R"(
  {
    "key": "key",
    "keyset": "keyset",
    "params": {
      "string_param": "St...",
        "localized_param": {
          "key": "second_key",
          "keyset": "second_keyset",
          "params": {
            "some_param": "so..."
          }
        },
        "array_param": ["st...", "ot..."],
        "number": "...",
        "null": null,
        "empty_string": "...",
        "string_1_len": "..."
    }
  }
  )");
  EXPECT_EQ(expected, utils::MaskText(input));
}

}  // namespace ucommunications
