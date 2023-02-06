#include <gtest/gtest.h>

#include "utils/utils.hpp"

namespace callcenter_stats::unit_tests {

class MaskUrlencodedFieldTests : public ::testing::Test {};

TEST_F(MaskUrlencodedFieldTests, TestEmpty) {
  const auto body = "";
  const auto& masked = utils::MaskUrlencodedField(body, "CALLERID");
  EXPECT_FALSE(masked.has_value());
}

TEST_F(MaskUrlencodedFieldTests, TestNoField) {
  const auto body = "mfwerwrewca=23232&werwfqwqf=12ds";
  const auto& masked = utils::MaskUrlencodedField(body, "CALLERID");
  EXPECT_FALSE(masked.has_value());
}

TEST_F(MaskUrlencodedFieldTests, TestBegin) {
  const auto body = "CALLERID=+79991111111&ORIGINAL_DN=+749599999999";
  const auto& masked = utils::MaskUrlencodedField(body, "CALLERID");
  EXPECT_TRUE(masked.has_value());
  EXPECT_EQ(masked.value(), "CALLERID=***&ORIGINAL_DN=+749599999999");
}

TEST_F(MaskUrlencodedFieldTests, TestMiddle) {
  const auto body =
      "ORIGINAL_DN=+749599999999&CALLERID=+79991111111&ORIGINAL_DN=+"
      "749599999999";
  const auto& masked = utils::MaskUrlencodedField(body, "CALLERID");
  EXPECT_TRUE(masked.has_value());
  EXPECT_EQ(masked.value(),
            "ORIGINAL_DN=+749599999999&CALLERID=***&ORIGINAL_DN=+749599999999");
}

TEST_F(MaskUrlencodedFieldTests, TestEnd) {
  const auto body = "ORIGINAL_DN=+749599999999&CALLERID=+79991111111";
  const auto& masked = utils::MaskUrlencodedField(body, "CALLERID");
  EXPECT_TRUE(masked.has_value());
  EXPECT_EQ(masked.value(), "ORIGINAL_DN=+749599999999&CALLERID=***");
}

}  // namespace callcenter_stats::unit_tests
