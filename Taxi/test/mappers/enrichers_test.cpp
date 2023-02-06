#include <userver/utest/utest.hpp>

#include <clients/rider-metrics-storage/client_mock_base.hpp>

#include <eventus/mappers/rms_history_test_mapper.hpp>

namespace {

using clients::rider_metrics_storage::CommandControl;
using clients::rider_metrics_storage::HistoryEventData;
using clients::rider_metrics_storage::v1_events_history::post::Request;
using clients::rider_metrics_storage::v1_events_history::post::Response200;

class ClientMock final : public clients::rider_metrics_storage::ClientMockBase {
 public:
  Response200 V1EventsHistory(
      const Request& /*request*/,
      const CommandControl& /*command_control*/ = {}) const override {
    return Response200({});
  }
};

eventus::mappers::RmsHistoryMapper GetMapper(::ClientMock& client) {
  formats::json::ValueBuilder builder;
  builder["user_id"] = "default";
  return eventus::mappers::RmsHistoryMapper(
      client, builder.ExtractValue(),
      std::unordered_map<std::string, std::string>{
          {"created", "created_after"}},
      std::unordered_map<std::string, std::string>{{"events", "EVENTS"}});
}

void TestCase(eventus::mappers::RmsHistoryMapper& mapper,
              formats::json::Value before, formats::json::Value after) {
  eventus::mappers::Event event(before.Clone());

  mapper.Map(event);
  ASSERT_EQ(event.GetData(), after);
}

TEST(TestEnrichers, TestRmsHistoryMapper) {
  ::ClientMock client;
  auto mapper = GetMapper(client);

  formats::json::ValueBuilder before;
  before["created"] = "2020-11-09T07:25:11+0000";

  formats::json::ValueBuilder after;
  after["created"] = "2020-11-09T07:25:11+0000";
  after["EVENTS"] = std::vector<HistoryEventData>{};

  TestCase(mapper, before.ExtractValue(), after.ExtractValue());
}

}  // namespace
