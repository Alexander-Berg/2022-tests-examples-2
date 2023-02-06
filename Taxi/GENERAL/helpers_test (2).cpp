#include "helpers.hpp"

#include <gtest/gtest.h>

using models::feedbacks::TruncateStringUtf8;

TEST(ModelsFeedbacksHelpers, TruncateStringUtf) {
  EXPECT_STREQ(TruncateStringUtf8("John Smith", 4).c_str(), "John");
  EXPECT_STREQ(TruncateStringUtf8("John Smith", 5).c_str(), "John ");
  EXPECT_STREQ(TruncateStringUtf8("John Smith", 6).c_str(), "John S");
  EXPECT_STREQ(TruncateStringUtf8("John Smith", 30).c_str(), "John Smith");

  // Cyrillic - 2 bytes per symbol
  EXPECT_STREQ(TruncateStringUtf8("аб123в777", 0).c_str(), "");
  EXPECT_STREQ(TruncateStringUtf8("аб123в777", 1).c_str(), "");
  EXPECT_STREQ(TruncateStringUtf8("аб123в777", 5).c_str(), "аб1");
  EXPECT_STREQ(TruncateStringUtf8("аб123в777", 8).c_str(), "аб123");
  EXPECT_STREQ(TruncateStringUtf8("аб123в777", 9).c_str(), "аб123в");
  EXPECT_STREQ(TruncateStringUtf8("аб123в777", 32).c_str(), "аб123в777");

  EXPECT_STREQ(TruncateStringUtf8("Иванов Иван Иванович", 30).c_str(),
               "Иванов Иван Иван");
  EXPECT_STREQ(TruncateStringUtf8("Иванов Иван Иванович", 31).c_str(),
               "Иванов Иван Иван");
  EXPECT_STREQ(TruncateStringUtf8("Иванов Иван Иванович", 128).c_str(),
               "Иванов Иван Иванович");

  // Georgian - 3 bytes per symbol
  EXPECT_STREQ(TruncateStringUtf8("სოლოღაშვილი", 0).c_str(), "");
  EXPECT_STREQ(TruncateStringUtf8("სოლოღაშვილი", 1).c_str(), "");
  EXPECT_STREQ(TruncateStringUtf8("სოლოღაშვილი", 5).c_str(), "ს");
  EXPECT_STREQ(TruncateStringUtf8("სოლოღაშვილი", 10).c_str(), "სოლ");
  EXPECT_STREQ(TruncateStringUtf8("სოლოღაშვილი", 32).c_str(), "სოლოღაშვილ");
  EXPECT_STREQ(TruncateStringUtf8("ს ო ლ ო ღ ა ", 10).c_str(), "ს ო ");
  EXPECT_STREQ(TruncateStringUtf8("ს ო ლ ო ღ ა ", 11).c_str(), "ს ო ლ");
  EXPECT_STREQ(TruncateStringUtf8("ს ო ლ ო ღ ა ", 12).c_str(), "ს ო ლ ");
  EXPECT_STREQ(TruncateStringUtf8("ს ო ლ ო ღ ა ", 13).c_str(), "ს ო ლ ");
  EXPECT_STREQ(TruncateStringUtf8("ს ო ლ ო ღ ა ", 14).c_str(), "ს ო ლ ");
  EXPECT_STREQ(TruncateStringUtf8("ს ო ლ ო ღ ა ", 15).c_str(), "ს ო ლ ო");

  // mix
  EXPECT_STREQ(TruncateStringUtf8("სოZZZ ", 5).c_str(), "ს");
  EXPECT_STREQ(TruncateStringUtf8("სოZZZ ", 6).c_str(), "სო");
  EXPECT_STREQ(TruncateStringUtf8("სოZZZ ", 7).c_str(), "სოZ");
  EXPECT_STREQ(TruncateStringUtf8("სოZZZ ", 8).c_str(), "სოZZ");
  EXPECT_STREQ(TruncateStringUtf8("სოZZZ ", 9).c_str(), "სოZZZ");

  EXPECT_STREQ(TruncateStringUtf8("სოლო раз ღაშვილი", 13).c_str(), "სოლო ");
  EXPECT_STREQ(TruncateStringUtf8("სოლო раз ღაშვილი", 15).c_str(), "სოლო р");
  EXPECT_STREQ(TruncateStringUtf8("სოლო раз ღაშვილი", 25).c_str(),
               "სოლო раз ღ");
  EXPECT_STREQ(TruncateStringUtf8("სოლო раз ღაშვილი", 30).c_str(),
               "სოლო раз ღაშ");
}
