#include <gtest/gtest.h>

#include "models/call_routing.hpp"

namespace callcenter_queues::unit_tests {

using namespace callcenter_queues::models::call_routing;

class SubclusterParametersTests : public ::testing::Test {};

TEST_F(SubclusterParametersTests, TestPriority) {
  SubclusterParameters params{"name", 10, 9, 2, 3};

  EXPECT_DOUBLE_EQ(params.GetPriority(), (9 - 2 - 3) / 10.0);
}

TEST_F(SubclusterParametersTests, TestJson) {
  SubclusterParameters params{"name", 10, 9, 2, 3};

  const auto& json_str = ToString(params.GetJson().ExtractValue());
  /*
     {"name":"name",
     "connected_agents":10,
     "queue_length":2,
     "routed_calls":3,
     "priority":"0.4"}
  */
  EXPECT_EQ(json_str,
            "{\"name\":\"name\","
            "\"connected_agents\":10,"
            "\"waiting_agents\":9,"
            "\"queue_length\":2,"
            "\"routed_calls\":3,"
            "\"priority\":0.4}");
}

}  // namespace callcenter_queues::unit_tests
