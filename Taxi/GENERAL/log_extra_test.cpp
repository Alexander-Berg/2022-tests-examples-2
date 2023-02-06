#include "log_extra.hpp"

#include <gtest/gtest.h>

using logging::internal::EncodeMode;

static std::string EncodeTskv(const std::string& str,
                              EncodeMode mode = EncodeMode::Key) {
  std::string to;
  logging::internal::EncodeTskv(to, str, mode);
  return to;
}

TEST(LogExtra, EncodeTskv) {
  // simple
  EXPECT_STREQ("\\=", EncodeTskv("=").c_str());
  EXPECT_STREQ("\\\\", EncodeTskv("\\").c_str());
  EXPECT_STREQ("\"", EncodeTskv("\"").c_str());
  EXPECT_STREQ("\\t", EncodeTskv("\t").c_str());
  EXPECT_STREQ("\\n", EncodeTskv("\n").c_str());
  EXPECT_STREQ("\\r", EncodeTskv("\r").c_str());
  EXPECT_STREQ("\\0", EncodeTskv(std::string("\0", 1)).c_str());

  EXPECT_STREQ("=", EncodeTskv("=", EncodeMode::Value).c_str());
  EXPECT_STREQ("\\\\", EncodeTskv("\\", EncodeMode::Value).c_str());
  EXPECT_STREQ("\"", EncodeTskv("\"", EncodeMode::Value).c_str());
  EXPECT_STREQ("\\t", EncodeTskv("\t", EncodeMode::Value).c_str());
  EXPECT_STREQ("\\n", EncodeTskv("\n", EncodeMode::Value).c_str());
  EXPECT_STREQ("\\r", EncodeTskv("\r", EncodeMode::Value).c_str());
  EXPECT_STREQ("\\0",
               EncodeTskv(std::string("\0", 1), EncodeMode::Value).c_str());

  // in text
  EXPECT_STREQ("Hello World!\\nHello World!",
               EncodeTskv("Hello World!\nHello World!").c_str());
  EXPECT_STREQ("a\\=1\\tb\\=2\\na+b\\=3",
               EncodeTskv("a=1\tb=2\na+b=3").c_str());

  EXPECT_STREQ(
      "Hello World!\\nHello World!",
      EncodeTskv("Hello World!\nHello World!", EncodeMode::Value).c_str());
  EXPECT_STREQ("a=1\\tb=2\\na+b=3",
               EncodeTskv("a=1\tb=2\na+b=3", EncodeMode::Value).c_str());

  // serial
  EXPECT_STREQ("\\\\\\\\\\=\\n\\tabc\\t\\n",
               EncodeTskv("\\\\=\n\tabc\t\n").c_str());
}

TEST(LogExtra, Stream) {
  std::string str;
  LogExtra({{"a=a", "a=a"}}).Serialize(str);
  LogExtra({{"\tb", "\\b\nb"}}).Serialize(str);
  EXPECT_STREQ("a\\=a=a=a\t\\tb=\\\\b\\nb\t", str.c_str());
}
