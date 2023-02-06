#include <gtest/gtest.h>
#include <fmt/format.h>

TEST(FmtTest, ValidFormat) {
  ASSERT_EQ("Hello world!", fmt::format("{} {}!", "Hello", "world"));
  ASSERT_EQ("abracadabra", fmt::format("{0}{1}{0}", "abra", "cad"));
  ASSERT_EQ("Running: test",
            fmt::format("Running: {cmd}", fmt::arg("cmd", "test")));
}

std::string get_key(const std::string& text) {
  return "test {" + text + "}";
}

std::wstring get_key(const std::wstring& text) {
  return L"test {" + text + L"}";
}

template<typename T>
void invalid_key(T key, std::string err_message) {
  T format_str = get_key(key);

  try {
    fmt::format(format_str, fmt::arg("invalid_key", "value"));
    FAIL()
    << "expected to get exception on invalid format string, but got nothing";
  }
  catch (const fmt::FormatError& e) {
    EXPECT_EQ(err_message, e.what());
  }
  catch (const std::exception& e) {
    FAIL() << "got unknown error with text: " << e.what();
  }
}

TEST(FmtTest, InvalidKeyFormat) {
  invalid_key(std::string("expected_key"), "argument not found - expected_key");
  invalid_key(std::wstring(L"expected_key"), "argument not found");
}
