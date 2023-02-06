#include "text_template.hpp"

#include <gtest/gtest.h>

TEST(TextTemplate, Dummy) {
  ff::TextTemplate tt("{one} {two} {three}");
  EXPECT_STREQ(
      "1 2 3",
      tt.SubstituteArgs({{"one", "1"}, {"two", "2"}, {"three", "3"}}).c_str());
}
