
#include <atomic>

#include <userver/utest/utest.hpp>

#include <clients/stq-agent/client_gmock.hpp>
#include <stq/client.hpp>
#include <testing/taxi_config.hpp>
#include <tvm2/utest/mock_client_context.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/http_client.hpp>

namespace {
using namespace clients::stq_agent;

struct ArgsStruct {
  std::string some_arg = "some_arg_value";
};

class CallManyMock : public deprecated::Client {
 public:
  using deprecated::Client::Client;

  std::string PerformRequest(
      const std::string& split_id, const std::string& queue_name,
      const std::string& path, std::string body,
      std::optional<int> /* retries */ = std::nullopt) const override {
    ++ncalls;

    EXPECT_EQ(split_id, "some_task_id1");
    EXPECT_EQ(queue_name, "abacaba_queue");
    EXPECT_EQ(path, "/queues/api/add/abacaba_queue/bulk");
    auto tasks = formats::json::FromString(body)["tasks"];
    EXPECT_EQ(tasks.GetSize(), 2);
    EXPECT_EQ(tasks[0]["task_id"].As<std::string>(), "some_task_id1");
    EXPECT_EQ(tasks[0]["args"][0].As<std::string>(), "some_arg_value");
    EXPECT_EQ(tasks[1]["task_id"].As<std::string>(), "some_task_id2");
    EXPECT_EQ(tasks[1]["args"][0].As<std::string>(), "some_arg_value");

    return R"({"tasks":[
      {"task_id":"some_task_id1",
       "add_result":{"code":500,"description":"some error description 1"}},
      {"task_id":"some_task_id2",
       "add_result":{"code":500,"description":"some error description 2"}}
    ]})";
  }

  mutable std::atomic_size_t ncalls = 0;
};

}  // namespace
namespace stq {
template <>
stq::TaskArguments<formats::json::Value> Serialize(ArgsStruct&& args) {
  stq::TaskArguments<formats::json::Value> res;
  res.args = formats::json::MakeArray(std::move(args.some_arg));
  return res;
}
}  // namespace stq

UTEST(StqClient, BulkTaskAddFail) {
  auto http_client = utest::CreateHttpClient();
  tvm2::utest::MockClientContext tvm2_context(*http_client);
  CallManyMock call_many_mock_client(dynamic_config::GetDefaultSource(),
                                     tvm2_context, "only_bulk!");

  ClientGMock gmock;
  stq::BaseQueueClient base_client(call_many_mock_client, gmock,
                                   "abacaba_queue");

  stq::QueueClient<ArgsStruct, formats::json::Value> queue_client(base_client);

  stq::impl::CallManyBuilder<ArgsStruct, formats::json::Value> builder;
  builder.AddCall("some_task_id1", {});
  builder.AddCall("some_task_id2", {});
  auto result = queue_client.CallMany(std::move(builder));

  EXPECT_EQ(result.failed.size(), 2);
  EXPECT_EQ(result.failed["some_task_id1"], "some error description 1");
  EXPECT_EQ(result.failed["some_task_id2"], "some error description 2");
  EXPECT_EQ(call_many_mock_client.ncalls, 1);
}
