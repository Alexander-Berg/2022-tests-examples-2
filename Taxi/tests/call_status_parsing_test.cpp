#include <gtest/gtest.h>

#include <chrono>
#include <optional>

#include <userver/utils/mock_now.hpp>

#include "messages_data.hpp"
#include "models/call.hpp"
#include "utils/utils.hpp"

namespace callcenter_stats::unit_tests {
using TimePoint = std::chrono::system_clock::time_point;

class CallStatusParsing : public MessagesData {
 protected:
  models::call::CallStatus meta_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "disp_cc",
      models::call::kMeta,
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::nullopt,
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::nullopt,
      std::nullopt,
      std::nullopt};
  models::call::CallStatus enter_queue_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "disp_cc",
      models::call::kQueued,
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::optional<std::string>{"+79872676410"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::nullopt,
      std::nullopt,
      std::nullopt};
  models::call::CallStatus connect_call{
      "taxi-myt-qapp1.yndx.net-1500000000.0000",
      "disp_cc",
      models::call::kTalking,
      utils::TimePoint(std::chrono::seconds(1500000001)),
      std::optional<std::string>{"0002040101-0000065536-1582274287-0000030555"},
      std::optional<std::string>{"+74832220220"},
      std::optional<std::string>{"+79872676410"},
      utils::TimePoint(std::chrono::seconds(1500000000)),
      std::optional<TimePoint>(
          utils::TimePoint(std::chrono::seconds(1500000001))),
      std::optional<std::string>{"1000001287"},
      std::nullopt};
};

TEST_F(CallStatusParsing, TestMeta) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(
      models::call::ExtractCallStatus(
          kCallId, {utils::ParseQappEvent(qapp_event["META"])}, pd_id_mapping),
      meta_call);
}

TEST_F(CallStatusParsing, TestEnterQueue) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(models::call::ExtractCallStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"])},
                pd_id_mapping),
            enter_queue_call);
}

TEST_F(CallStatusParsing, TestConnect) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(models::call::ExtractCallStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["CONNECT"])},
                pd_id_mapping),
            connect_call);
}

TEST_F(CallStatusParsing, TestMetaAfterTransfer) {
  ::utils::datetime::MockNowSet(kMockTime);
  EXPECT_EQ(models::call::ExtractCallStatus(
                kCallId,
                {utils::ParseQappEvent(qapp_event["META"]),
                 utils::ParseQappEvent(qapp_event["ENTERQUEUE"]),
                 utils::ParseQappEvent(qapp_event["CONNECT"]),
                 utils::ParseQappEvent(qapp_event["BLINDTRANSFER"]),
                 utils::ParseQappEvent(qapp_event["META"])},
                pd_id_mapping),
            meta_call);
}

}  // namespace callcenter_stats::unit_tests
