#include <gtest/gtest.h>

#include "exceptions.hpp"
#include "utils/utils.hpp"

namespace callcenter_queues::unit_tests {

class AgentIdParsing : public ::testing::Test {
 protected:
  std::unordered_map<std::string, std::string> agent_ids{
      {"Agent/1000002656", "1000002656"},
      {"Local/1000004572@CC_AGENTS/n", "1000004572"}};
};

TEST_F(AgentIdParsing, Test1) {
  EXPECT_EQ(utils::ParseAgentId("Agent/1000002656"), "1000002656");
}

TEST_F(AgentIdParsing, Test2) {
  EXPECT_EQ(utils::ParseAgentId("Local/1000004572@CC_AGENTS/n"), "1000004572");
}

TEST_F(AgentIdParsing, Test3) {
  EXPECT_EQ(utils::ParseAgentId(""), "bad_agent_id");
}

TEST_F(AgentIdParsing, Test4) {
  EXPECT_EQ(utils::ParseAgentId("John"), "bad_agent_id");
}

TEST_F(AgentIdParsing, Test5) {
  EXPECT_EQ(utils::ParseAgentId("1000002656"), "bad_agent_id");
}

}  // namespace callcenter_queues::unit_tests
