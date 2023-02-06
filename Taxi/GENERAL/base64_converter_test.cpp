#include "base64_converter.hpp"

#include <gtest/gtest.h>

#include <iostream>

namespace eats_restapp_marketing::helpers {

const std::string test_value_base64 =
    "data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=";

const std::string test_value = "cXFxcXdxZXJxZXJxZXI=";

const std::string expected_value = "qqqqwqerqerqer";

TEST(convert_base64_helper, without_prefix) {
  auto result = helpers::ConvertImageFromBase64(test_value).value();

  ASSERT_EQ(result, expected_value);
}

TEST(convert_base64_helper, with_prefix) {
  ASSERT_EQ(helpers::ConvertImageFromBase64(test_value_base64,
                                            "data:image/jpeg;base64,")
                .value(),
            expected_value);
}

}  // namespace eats_restapp_marketing::helpers
