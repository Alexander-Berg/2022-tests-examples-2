#include <gtest/gtest.h>

#include <string>
#include <vector>

#include "utils/utils.hpp"

namespace callcenter_queues::unit_tests {

class JoinWithLimitTests : public ::testing::Test {
 protected:
  std::vector<std::string> empty_items{};

  std::vector<std::string> items{"item1", "item2", "item3"};

  void checkJoinItems(std::string::size_type limit,
                      std::string expected_result) {
    auto result = utils::JoinWithLimit(items, limit, ", ", "...");
    EXPECT_LE(result.length(), limit);
    EXPECT_EQ(result, expected_result);
  }
};

TEST_F(JoinWithLimitTests, TestEmptyItems) {
  EXPECT_EQ(utils::JoinWithLimit(empty_items, 0, "", ""), "");
}

TEST_F(JoinWithLimitTests, TestLimit1) { checkJoinItems(1, ""); }

TEST_F(JoinWithLimitTests, TestLimit3) { checkJoinItems(3, "..."); }

TEST_F(JoinWithLimitTests, TestLimit5) { checkJoinItems(5, "..."); }

TEST_F(JoinWithLimitTests, TestLimit7) { checkJoinItems(5 + 2, "..."); }

TEST_F(JoinWithLimitTests, TestLimit10) {
  checkJoinItems(5 + 2 + 3, "item1, ...");
}

TEST_F(JoinWithLimitTests, TestLimit12) {
  checkJoinItems(5 + 2 + 5, "item1, ...");
}
TEST_F(JoinWithLimitTests, TestLimit17) {
  checkJoinItems(5 + 2 + 5 + 2 + 3, "item1, item2, ...");
}

TEST_F(JoinWithLimitTests, TestLimit19) {
  checkJoinItems(5 + 2 + 5 + 2 + 5, "item1, item2, item3");
}
}  // namespace callcenter_queues::unit_tests
