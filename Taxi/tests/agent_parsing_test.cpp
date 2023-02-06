#include <gtest/gtest.h>

#include <chrono>
#include <optional>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>

#include "messages_data.hpp"
#include "models/agent.hpp"
#include "utils/utils.hpp"

namespace callcenter_stats::unit_tests {

class AgentParsing : public MessagesData {
 protected:
  models::agent::AgentTalkingStatus connect_agent{
      "1000001287", utils::TimePoint(std::chrono::seconds(1500000001)),
      true,         std::string("disp_cc"),
      std::nullopt,
  };
  models::agent::AgentTalkingStatus complete_caller_agent{
      "1000001287",
      utils::TimePoint(std::chrono::seconds(1500000002)),
      false,
      std::string("disp_cc"),
      utils::TimePoint(std::chrono::seconds(1500000012)),
  };
  models::agent::AgentTalkingStatus complete_agent_agent{
      "1000001287",
      utils::TimePoint(std::chrono::seconds(1500000002)),
      false,
      std::string("disp_cc"),
      utils::TimePoint(std::chrono::seconds(1500000012)),
  };
  models::agent::AgentTalkingStatus blindtransfer_agent{
      "1000001287",
      utils::TimePoint(std::chrono::seconds(1500000002)),
      false,
      std::string("disp_cc"),
      utils::TimePoint(std::chrono::seconds(1500000012)),
  };
  models::agent::AgentTalkingStatus attendedransfer_agent{
      "1000001287",
      utils::TimePoint(std::chrono::seconds(1500000002)),
      false,
      std::string("disp_cc"),
      utils::TimePoint(std::chrono::seconds(1500000012)),
  };
  const std::string delimiter = "_on_";
  ::dynamic_config::ValueDict<std::chrono::seconds>
      postcall_processing_time_map{"name",
                                   {{"__default__", std::chrono::seconds{10}}}};
};

TEST_F(AgentParsing, TestConnect) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["CONNECT"])},
                delimiter, postcall_processing_time_map),
            connect_agent);
}

TEST_F(AgentParsing, TestCompleteCaller) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["CONNECT"]),
                 utils::ParseQappEvent(qapp_event["COMPLETECALLER"])},
                delimiter, postcall_processing_time_map),
            complete_caller_agent);
}

TEST_F(AgentParsing, TestCompleteAgent) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["CONNECT"]),
                 utils::ParseQappEvent(qapp_event["COMPLETEAGENT"])},
                delimiter, postcall_processing_time_map),
            complete_agent_agent);
}

TEST_F(AgentParsing, TestBlindTransfer) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["CONNECT"]),
                 utils::ParseQappEvent(qapp_event["BLINDTRANSFER"])},
                delimiter, postcall_processing_time_map),
            blindtransfer_agent);
}
TEST_F(AgentParsing, TestAttendedTransfer) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["CONNECT"]),
                 utils::ParseQappEvent(qapp_event["ATTENDEDTRANSFER"])},
                delimiter, postcall_processing_time_map),
            attendedransfer_agent);
}

TEST_F(AgentParsing, TestAbandon) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["ABANDON"])},
                delimiter, postcall_processing_time_map),
            std::nullopt);
}
TEST_F(AgentParsing, TestEnterQueue) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"])},
                delimiter, postcall_processing_time_map),
            std::nullopt);
}
TEST_F(AgentParsing, TestRingNoAnswer) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["RINGNOANSWER"])},
                delimiter, postcall_processing_time_map),
            std::nullopt);
}
TEST_F(AgentParsing, TestRingCanceled) {
  EXPECT_EQ(models::agent::ExtractAgentTalkingStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["RINGCANCELED"])},
                delimiter, postcall_processing_time_map),
            std::nullopt);
}

}  // namespace callcenter_stats::unit_tests
