#include <gtest/gtest.h>

#include <access-control-info/models/parsed_http_request.hpp>

namespace access_control_info {

bool TestParse(const std::string& query, const models::Query& expected) {
  auto result = models::ParseArgs(query);
  return result == expected;
}

TEST(TestParseArgs, Test1) {
  bool test{false};

  test = TestParse("par_a=1&par_b=2", {{"par_a", {"1"}}, {"par_b", {"2"}}});
  EXPECT_TRUE(test);

  test = TestParse("par_a=1&par_b=2&par_a=3",
                   {{"par_a", {"1", "3"}}, {"par_b", {"2"}}});
  EXPECT_TRUE(test);

  test = TestParse("par_a=1&par_a=32&par_b=2",
                   {{"par_a", {"1", "32"}}, {"par_b", {"2"}}});
  EXPECT_TRUE(test);

  test = TestParse("par_a=12&par_a=3&par_b=23",
                   {{"par_a", {"12", "3"}}, {"par_b", {"23"}}});
  EXPECT_TRUE(test);

  test = TestParse("par", {{"par", {""}}});
  EXPECT_TRUE(test);

  test = TestParse("par1&par2", {{"par1", {""}}, {"par2", {""}}});
  EXPECT_TRUE(test);

  test = TestParse("par1&par2", {{"par1", {""}}, {"par2", {""}}});
  EXPECT_TRUE(test);

  test = TestParse("par1&par_b=2", {{"par1", {""}}, {"par_b", {"2"}}});
  EXPECT_TRUE(test);

  test = TestParse("b=3&p&b=2", {{"p", {""}}, {"b", {"3", "2"}}});
  EXPECT_TRUE(test);

  test = TestParse("par2&par_a=55&b=3&par1&b=2&c=6", {{"par1", {""}},
                                                      {"par2", {""}},
                                                      {"par_a", {"55"}},
                                                      {"c", {"6"}},
                                                      {"b", {"3", "2"}}});

  test = TestParse("=&par_b&&=&=lkjl&par_a=2",
                   {{"par_b", {""}}, {"par_a", {"2"}}});
  EXPECT_TRUE(test);
}

}  // namespace access_control_info
