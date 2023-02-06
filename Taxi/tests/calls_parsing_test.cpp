#include <userver/utest/utest.hpp>

#include <chrono>
#include <optional>

#include <testing/taxi_config.hpp>
#include <userver/utils/mock_now.hpp>

#include "messages_data.hpp"
#include "models/call.hpp"
#include "models/factories/call_factory.hpp"
#include "test_personal_client.hpp"
#include "utils/utils.hpp"

namespace callcenter_queues::unit_tests {
using TimePoint = std::chrono::system_clock::time_point;

// disp_cc queue is parsed for metaqueue disp and subcluster cc
// in stable correct queue example is ru_taxi_disp_on_1 with delimiter _on_
class CallsParsing : public MessagesData {
 protected:
  models::call::Call enter_queue_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "commutation_id",
      "disp",
      "cc",
      models::call::kQueued,
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::optional<std::string>{"+79872676410"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
  };
  models::call::Call connect_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "commutation_id",
      "disp",
      "cc",
      models::call::kTalking,
      utils::TimePoint(std::chrono::seconds(1500000001)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::optional<std::string>{"+79872676410"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000001))),
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::optional<std::string>{"1000001287"}};
  models::call::Call complete_caller_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "commutation_id",
      "disp",
      "cc",
      models::call::kCompleted,
      utils::TimePoint(std::chrono::seconds(1500000002)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::optional<std::string>{"+79872676410"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000001))),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000002))),
      std::optional<std::string>{models::call::kCompletedByCaller},
      std::nullopt,
      std::optional<std::string>{"1000001287"}};
  models::call::Call complete_agent_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "commutation_id",
      "disp",
      "cc",
      models::call::kCompleted,
      utils::TimePoint(std::chrono::seconds(1500000002)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::optional<std::string>{"+79872676410"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000001))),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000002))),
      std::optional<std::string>{models::call::kCompletedByAgent},
      std::nullopt,
      std::optional<std::string>{"1000001287"}};
  models::call::Call blind_transfer_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "commutation_id",
      "disp",
      "cc",
      models::call::kCompleted,
      utils::TimePoint(std::chrono::seconds(1500000002)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::optional<std::string>{"+79872676410"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000001))),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000002))),
      std::optional<std::string>{models::call::kTransfered},
      std::optional<std::string>{"8002"},
      std::optional<std::string>{"1000001287"}};
  models::call::Call attended_transfer_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "commutation_id",
      "disp",
      "cc",
      models::call::kCompleted,
      utils::TimePoint(std::chrono::seconds(1500000002)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::optional<std::string>{"+79872676410"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000001))),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000002))),
      std::optional<std::string>{models::call::kTransfered},
      std::nullopt,
      std::optional<std::string>{"1000001287"}};
};

UTEST_F(CallsParsing, TestEnterQueue) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(callcenter_queues::models::call::CallFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"])},
                pd_id_mapping, "_")
                .Extract()
                .value(),
            enter_queue_call);
}

UTEST_F(CallsParsing, TestConnect) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(callcenter_queues::models::call::CallFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"])},
                pd_id_mapping, "_")
                .Extract()
                .value(),
            connect_call);
}

UTEST_F(CallsParsing, TestCompleteAgent) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(callcenter_queues::models::call::CallFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"]),
                 utils::ParseQprocEvent(qproc_event["COMPLETEAGENT"])},
                pd_id_mapping, "_")
                .Extract()
                .value(),
            complete_agent_call);
}
UTEST_F(CallsParsing, TestCompleteCaller) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(callcenter_queues::models::call::CallFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"]),
                 utils::ParseQprocEvent(qproc_event["COMPLETECALLER"])},
                pd_id_mapping, "_")
                .Extract()
                .value(),
            complete_caller_call);
}
UTEST_F(CallsParsing, TestBlindTransfer) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(callcenter_queues::models::call::CallFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"]),
                 utils::ParseQprocEvent(qproc_event["BLINDTRANSFER"])},
                pd_id_mapping, "_")
                .Extract()
                .value(),
            blind_transfer_call);
}

UTEST_F(CallsParsing, TestAttendedTransfer) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(callcenter_queues::models::call::CallFactory(
                kCallId,
                {utils::ParseQprocEvent(qproc_event["META"]),
                 utils::ParseQprocEvent(qproc_event["ENTERQUEUE"]),
                 utils::ParseQprocEvent(qproc_event["CONNECT"]),
                 utils::ParseQprocEvent(qproc_event["ATTENDEDTRANSFER"])},
                pd_id_mapping, "_")
                .Extract()
                .value(),
            attended_transfer_call);
}
}  // namespace callcenter_queues::unit_tests
