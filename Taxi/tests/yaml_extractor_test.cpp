#include "yaml_extractor.hpp"

#include "load_config_duration_parse.hpp"

#include <sstream>

#include <gtest/gtest.h>

TEST(YamlExtractor, Basic) {
  std::istringstream iss{R"(
    - text: hello
      bools: false
      seconds: 86400
    - text: word
      bools: true
      seconds: 860
    )"};

  utils::YamlExtractor extract(formats::yaml::FromStream(iss));
  auto it = extract.begin();
  std::string text;
  it->Extract("text", text);
  ASSERT_EQ(text, "hello");

  bool bools;
  it->Extract("bools", bools);
  ASSERT_FALSE(bools);

  std::chrono::seconds seconds;
  it->Extract("seconds", seconds);
  ASSERT_EQ(seconds, std::chrono::seconds(86400));

  ++it;

  it->Extract("text", text);
  ASSERT_EQ(text, "word");

  it->Extract("bools", bools);
  ASSERT_TRUE(bools);

  it->Extract("seconds", seconds);
  ASSERT_EQ(seconds, std::chrono::seconds(860));

  ++it;
  ASSERT_EQ(it, extract.end());
  ASSERT_NO_THROW(extract.EnsureFieldsAreExtracted());
}

TEST(YamlExtractor, Intervals) {
  std::istringstream iss{R"(
    val1: 3s
    val2: 1000ms
    val3: 2m
    val4: 2d
    val5: 2h
    val6: 7ms
  )"};

  utils::YamlExtractor e(formats::yaml::FromStream(iss));

  std::chrono::seconds sec;
  e.Extract("val1", sec);
  EXPECT_EQ(sec, std::chrono::seconds(3));

  e.Extract("val2", sec);
  EXPECT_EQ(sec, std::chrono::seconds(1));

  e.Extract("val3", sec);
  EXPECT_EQ(sec, std::chrono::seconds(120));

  std::chrono::hours hour;
  e.Extract("val4", hour);
  EXPECT_EQ(hour, std::chrono::hours(48));

  std::chrono::minutes min;
  e.Extract("val5", min);
  EXPECT_EQ(min, std::chrono::minutes(120));

  EXPECT_ANY_THROW(e.Extract("val6", min));
}

TEST(YamlExtractor, ImmediateThrowOnBadFormat) {
  std::istringstream iss{R"(
        text: hello
        bools: false
        seconds: 86400
        another_text: hello
      )"};

  utils::YamlExtractor extract(formats::yaml::FromStream(iss));
  ASSERT_ANY_THROW(extract.Extract<bool>("text"));
  ASSERT_ANY_THROW(extract.Extract<int>("another_text"));
  ASSERT_ANY_THROW(extract.Extract<bool>("seconds"));
}

TEST(YamlExtractor, ImmediateThrowOnNoField) {
  std::istringstream iss{"text: hello\nempty_seq:[]"};

  utils::YamlExtractor extract(formats::yaml::FromStream(iss));
  ASSERT_ANY_THROW(extract.Extract<bool>("does_not_exist"));
  ASSERT_ANY_THROW(extract.Extract<int>("does_not_exist"));
  ASSERT_ANY_THROW(extract.Extract<std::vector<int>>("does_not_exist"));
  ASSERT_ANY_THROW(extract.Extract<std::vector<int>>("empty_seq"));
}

TEST(YamlExtractor, ExtractKeepsTheValue) {
  std::istringstream iss;
  utils::YamlExtractor extract(formats::yaml::FromStream(iss));

  bool value = true;
  extract.OptionalExtract("bool_that_does_not_exist", value);
  ASSERT_TRUE(value);

  value = false;
  extract.OptionalExtract("bool_that_does_not_exist", value);
  ASSERT_FALSE(value);

  constexpr char long_string[] =
      "Some big string that must be kept by the YamlExtractor::Fill function";
  std::string str = long_string;
  extract.OptionalExtract("string_that_does_not_exist", str);
  ASSERT_EQ(str, long_string);
}

TEST(YamlExtractor, OneElementList) {
  std::istringstream iss{"- text"};

  utils::YamlExtractor extract(formats::yaml::FromStream(iss));
  extract.begin();
  ASSERT_ANY_THROW(extract.EnsureFieldsAreExtracted());
}

TEST(YamlExtractor, ErorrMessageInNotTooBig) {
  std::string s = "text: Some insanely huge string";
  constexpr unsigned yaml_string_size = 1024 * 4;
  s.resize(yaml_string_size, '!');
  std::istringstream iss{std::move(s)};
  utils::YamlExtractor extract(formats::yaml::FromStream(iss));

  std::string error_message;
  try {
    extract.EnsureFieldsAreExtracted();
  } catch (const std::exception& e) {
    error_message = e.what();
  }
  ASSERT_LT(error_message.size(), yaml_string_size);
  ASSERT_TRUE(error_message.find("<...>") != std::string::npos);
}

TEST(YamlExtractor, Anchors) {
  std::istringstream iss{R"(
    one: &entry
      text: hello
      bools: false
      seconds: 86400
    two: *entry
  )"};

  utils::YamlExtractor extractor(formats::yaml::FromStream(iss));
  auto one = extractor.ExtractSubTree("one");
  auto two = extractor.ExtractSubTree("two");

  EXPECT_EQ(one.Extract<std::string>("text"), two.Extract<std::string>("text"));
  EXPECT_EQ(one.Extract<bool>("bools"), two.Extract<bool>("bools"));
  EXPECT_EQ(one.Extract<std::chrono::seconds>("seconds"),
            two.Extract<std::chrono::seconds>("seconds"));

  ASSERT_NO_THROW(extractor.EnsureFieldsAreExtracted());
}
