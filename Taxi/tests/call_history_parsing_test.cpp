#include <gtest/gtest.h>

#include <chrono>
#include <optional>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utils/mock_now.hpp>

#include "messages_data.hpp"
#include "models/call.hpp"

namespace callcenter_stats::unit_tests {

class CallHistoryParsing : public MessagesData {
 protected:
  models::call::CallHistory abandon_call{
      "Zspdn7IdulP6h7X+gk8VeFlooh8=",
      utils::TimePoint(std::chrono::seconds(1500000004)),
      std::optional<std::string>("0002040101-0000065536-1582274287-0000030555"),
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "disp_cc",
      std::optional<std::string>("+79872676410"),
      std::nullopt,
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::nullopt,
      utils::TimePoint(std::chrono::seconds(1500000001)),
      models::call::CallHistoryEndreason::kAbandoned,
      std::nullopt,
      std::nullopt,
      std::optional<std::string>("+74832220220"),
      std::nullopt,
      std::nullopt,
      std::nullopt};
  models::call::CallHistory complete_caller_call{
      "DzOIGFTSeGVyq+MoUOKe6kWAbb0=",
      utils::TimePoint(std::chrono::seconds(1500000004)),
      std::optional<std::string>("0002040101-0000065536-1582274287-0000030555"),
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "disp_cc",
      std::optional<std::string>("+79872676410"),
      std::optional<std::string>{"1000001287"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      utils::TimePoint(std::chrono::seconds(1500000001)),
      utils::TimePoint(std::chrono::seconds(1500000002)),
      models::call::CallHistoryEndreason::kCompletedByCaller,
      std::nullopt,
      std::nullopt,
      std::optional<std::string>("+74832220220"),
      utils::TimePoint(std::chrono::seconds(1500000012)),
      std::nullopt,
      std::nullopt};
  models::call::CallHistory complete_agent_call{
      "LAZOv0oftXPw5tm2m3TJGSBbiOo=",
      utils::TimePoint(std::chrono::seconds(1500000004)),
      std::optional<std::string>("0002040101-0000065536-1582274287-0000030555"),
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "disp_cc",
      std::optional<std::string>("+79872676410"),
      std::optional<std::string>{"1000001287"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      utils::TimePoint(std::chrono::seconds(1500000001)),
      utils::TimePoint(std::chrono::seconds(1500000002)),
      models::call::CallHistoryEndreason::kCompletedByAgent,
      std::nullopt,
      std::nullopt,
      std::optional<std::string>("+74832220220"),
      utils::TimePoint(std::chrono::seconds(1500000012)),
      std::nullopt,
      std::nullopt};
  models::call::CallHistory blindtransfer_call{
      "V+M14vPOYhKGj9gjhyvR8//Z2zI=",
      utils::TimePoint(std::chrono::seconds(1500000004)),
      std::optional<std::string>("0002040101-0000065536-1582274287-0000030555"),
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "disp_cc",
      std::optional<std::string>("+79872676410"),
      std::optional<std::string>{"1000001287"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      utils::TimePoint(std::chrono::seconds(1500000001)),
      utils::TimePoint(std::chrono::seconds(1500000002)),
      models::call::CallHistoryEndreason::kTransfered,
      std::optional<std::string>{"help"},
      std::optional<std::string>{"8002"},
      std::optional<std::string>("+74832220220"),
      utils::TimePoint(std::chrono::seconds(1500000012)),
      std::nullopt,
      std::nullopt};
  models::call::CallHistory attendedtransfer_call{
      "V+M14vPOYhKGj9gjhyvR8//Z2zI=",
      utils::TimePoint(std::chrono::seconds(1500000004)),
      std::optional<std::string>("0002040101-0000065536-1582274287-0000030555"),
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "disp_cc",
      std::optional<std::string>("+79872676410"),
      std::optional<std::string>{"1000001287"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      utils::TimePoint(std::chrono::seconds(1500000001)),
      utils::TimePoint(std::chrono::seconds(1500000002)),
      models::call::CallHistoryEndreason::kTransfered,
      std::nullopt,
      std::nullopt,
      std::optional<std::string>("+74832220220"),
      utils::TimePoint(std::chrono::seconds(1500000012)),
      std::nullopt,
      std::nullopt};
  ::dynamic_config::ValueDict<std::string> transfer_map{
      "name", {{"__default__", "default"}, {"8002", "help"}}};
  const std::string delimiter = "_on_";
  ::dynamic_config::ValueDict<std::chrono::seconds>
      postcall_processing_time_map{"name",
                                   {{"__default__", std::chrono::seconds{10}}}};
};

TEST_F(CallHistoryParsing, TestEnterQueue) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .size(),
      0);
}

TEST_F(CallHistoryParsing, TestAbandon) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
           utils::ParseQappEvent(qapp_event["ABANDON"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .front(),
      abandon_call);
}

TEST_F(CallHistoryParsing, TestRingCanceled) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
           utils::ParseQappEvent(qapp_event["RINGCANCELED"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .size(),
      0);
}

TEST_F(CallHistoryParsing, TestRingNoAnswer) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
           utils::ParseQappEvent(qapp_event["RINGNOANSWER"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .size(),
      0);
}

TEST_F(CallHistoryParsing, TestConnect) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
           utils::ParseQappEvent(qapp_event["CONNECT"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .size(),
      0);
}

TEST_F(CallHistoryParsing, TestCompleteCaller) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
           utils::ParseQappEvent(qapp_event["CONNECT"]),
           utils::ParseQappEvent(qapp_event["COMPLETECALLER"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .front(),
      complete_caller_call);
}

TEST_F(CallHistoryParsing, TestCompleteAgent) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
           utils::ParseQappEvent(qapp_event["CONNECT"]),
           utils::ParseQappEvent(qapp_event["COMPLETEAGENT"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .front(),
      complete_agent_call);
}

TEST_F(CallHistoryParsing, TestBlindTransfer) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
           utils::ParseQappEvent(qapp_event["CONNECT"]),
           utils::ParseQappEvent(qapp_event["BLINDTRANSFER"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .front(),
      blindtransfer_call);
}

TEST_F(CallHistoryParsing, TestAttendedTransfer) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId,
          {utils::ParseQappEvent(qapp_event["META"]),
           utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
           utils::ParseQappEvent(qapp_event["CONNECT"]),
           utils::ParseQappEvent(qapp_event["ATTENDEDTRANSFER"])},
          transfer_map, delimiter, postcall_processing_time_map, pd_id_mapping)
          .front(),
      attendedtransfer_call);
}

TEST_F(CallHistoryParsing, TestMeta) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallHistory(
          kCallId, {utils::ParseQappEvent(qapp_event["META"])}, transfer_map,
          delimiter, postcall_processing_time_map, pd_id_mapping)
          .size(),
      0);
}

TEST_F(CallHistoryParsing, TestIds) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(abandon_call.CalculateId(), abandon_call.id);
  EXPECT_EQ(complete_caller_call.CalculateId(), complete_caller_call.id);
  EXPECT_EQ(complete_agent_call.CalculateId(), complete_agent_call.id);
  EXPECT_EQ(blindtransfer_call.CalculateId(), blindtransfer_call.id);
  EXPECT_EQ(attendedtransfer_call.CalculateId(), attendedtransfer_call.id);
}

}  // namespace callcenter_stats::unit_tests
