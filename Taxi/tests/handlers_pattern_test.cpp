#include <gtest/gtest.h>

#include <boost/regex.hpp>
#include <handlers/events/base.hpp>
#include <handlers/zone/byname.hpp>

TEST(RegexPattern, ByZone) {
  static const boost::regex expression(
      zone::ByNameHandler::kHandlerRegexPattern);
  boost::cmatch what;

  std::string test_string1 = "/zonename";
  EXPECT_EQ(boost::regex_match(test_string1.c_str(), what, expression), true);
  EXPECT_EQ(std::string(what[1]), std::string("zonename"));

  std::string test_string2 = "/zone_name";
  EXPECT_EQ(boost::regex_match(test_string2.c_str(), what, expression), true);
  EXPECT_EQ(std::string(what[1]), std::string("zone_name"));

  std::string test_string3 = "/zone-name";
  EXPECT_EQ(boost::regex_match(test_string3.c_str(), what, expression), true);
  EXPECT_EQ(std::string(what[1]), std::string("zone-name"));
}

TEST(RegexPattern, EventsBase) {
  static const boost::regex expression(
      events::BaseHandler::kHandlerRegexPattern);
  boost::cmatch what;

  std::string test_string1 = "/zonename/state";
  EXPECT_EQ(boost::regex_match(test_string1.c_str(), what, expression), true);
  EXPECT_EQ(std::string(what[1]), std::string("zonename"));

  std::string test_string2 = "/zone_name/state";
  EXPECT_EQ(boost::regex_match(test_string2.c_str(), what, expression), true);
  EXPECT_EQ(std::string(what[1]), std::string("zone_name"));

  std::string test_string3 = "/zone-name/state";
  EXPECT_EQ(boost::regex_match(test_string3.c_str(), what, expression), true);
  EXPECT_EQ(std::string(what[1]), std::string("zone-name"));
}
