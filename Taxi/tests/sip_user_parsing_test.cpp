#include <gtest/gtest.h>

#include <chrono>
#include <optional>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>

#include "messages_data.hpp"
#include "models/factories/sip_user_talking_queue_status_factory.hpp"
#include "models/sip_user.hpp"
#include "utils/utils.hpp"

namespace callcenter_queues::unit_tests {

class AgentParsing : public MessagesData {
 protected:
  models::sip_user::TalkingQueueStatus connect_agent{
      "1000001287",
      true,
      std::string("disp"),
      std::string("cc"),
      utils::TimePoint(std::chrono::seconds(1500000001)),
      std::nullopt,
      std::optional<std::string>("taxi-myt-qapp1.yndx.net-1500000000.0000")};
  models::sip_user::TalkingQueueStatus complete_caller_agent{
      "1000001287",
      false,
      std::string("disp"),
      std::string("cc"),
      utils::TimePoint(std::chrono::seconds(1500000002)),
      utils::TimePoint(std::chrono::seconds(1500000012)),
      std::nullopt};
  models::sip_user::TalkingQueueStatus complete_agent_agent{
      "1000001287",
      false,
      std::string("disp"),
      std::string("cc"),
      utils::TimePoint(std::chrono::seconds(1500000002)),
      utils::TimePoint(std::chrono::seconds(1500000012)),
      std::nullopt};
  models::sip_user::TalkingQueueStatus blindtransfer_agent{
      "1000001287",
      false,
      std::string("disp"),
      std::string("cc"),
      utils::TimePoint(std::chrono::seconds(1500000002)),
      utils::TimePoint(std::chrono::seconds(1500000012)),
      std::nullopt};
  models::sip_user::TalkingQueueStatus attendedransfer_agent{
      "1000001287",
      false,
      std::string("disp"),
      std::string("cc"),
      utils::TimePoint(std::chrono::seconds(1500000002)),
      utils::TimePoint(std::chrono::seconds(1500000012)),
      std::nullopt};
  const std::string delimiter = "_";
  ::dynamic_config::ValueDict<std::chrono::seconds>
      postcall_processing_time_map{"name",
                                   {{"__default__", std::chrono::seconds{10}}}};
};

TEST_F(AgentParsing, TestConnect) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"])},
                delimiter, postcall_processing_time_map)
                .Extract()
                .value(),
            connect_agent);
}

TEST_F(AgentParsing, TestCompleteCaller) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"]),
                 utils::ParseQprocEvent(qproc_event["COMPLETECALLER"])},
                delimiter, postcall_processing_time_map)
                .Extract()
                .value(),
            complete_caller_agent);
}

TEST_F(AgentParsing, TestCompleteAgent) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"]),
                 utils::ParseQprocEvent(qproc_event["COMPLETEAGENT"])},
                delimiter, postcall_processing_time_map)
                .Extract()
                .value(),
            complete_agent_agent);
}

TEST_F(AgentParsing, TestBlindTransfer) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"]),
                 utils::ParseQprocEvent(qproc_event["BLINDTRANSFER"])},
                delimiter, postcall_processing_time_map)
                .Extract()
                .value(),
            blindtransfer_agent);
}
TEST_F(AgentParsing, TestAttendedTransfer) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"]),
                 utils::ParseQprocEvent(qproc_event["ATTENDEDTRANSFER"])},
                delimiter, postcall_processing_time_map)
                .Extract()
                .value(),
            attendedransfer_agent);
}

TEST_F(AgentParsing, TestAbandon) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["ABANDON"])},
                delimiter, postcall_processing_time_map)
                .Extract(),
            std::nullopt);
}
TEST_F(AgentParsing, TestEnterQueue) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"])},
                delimiter, postcall_processing_time_map)
                .Extract(),
            std::nullopt);
}
TEST_F(AgentParsing, TestRingNoAnswer) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["RINGNOANSWER"])},
                delimiter, postcall_processing_time_map)
                .Extract(),
            std::nullopt);
}
TEST_F(AgentParsing, TestRingCanceled) {
  EXPECT_EQ(models::sip_user::TalkingStatusFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["RINGCANCELED"])},
                delimiter, postcall_processing_time_map)
                .Extract(),
            std::nullopt);
}

}  // namespace callcenter_queues::unit_tests
