#include <fmt/format.h>

#include <userver/formats/json/value_builder.hpp>
#include <userver/utest/utest.hpp>

#include <memory>
#include <string>
#include <vector>

#include <eventus/common/operation_argument.hpp>
#include <eventus/operations/basic/filters/equal_filters/string_equal_filter/string_equal_filter.hpp>
#include <eventus/operations/basic/filters/string_array_filter/string_array_filter.hpp>
#include <eventus/operations/filter_base.hpp>
#include <eventus/pipeline/event.hpp>
#include <eventus/pipeline/fanout.hpp>
#include <eventus/pipeline/node_builder_utils.hpp>
#include <eventus/pipeline/operation.hpp>
#include <eventus/pipeline/sink.hpp>
#include <eventus/pipeline/test_helpers.hpp>
#include <eventus/sinks/basic/log_sink.hpp>

namespace {

auto MakeTestFilterNode(const std::string& node_name,
                        eventus::filters::FilterTypePtr filter_ptr) {
  auto operation = eventus::pipeline::FilterOperation::Make(
      eventus::filters::CreateIsEventAcceptedFunc(filter_ptr));
  return eventus::pipeline::MakeNode(node_name, std::move(operation),
                                     eventus::pipeline::MakeTestErrorHandler());
};

}  // namespace

UTEST(PipelineSuite, FanoutTest) {
  auto fanout = std::make_shared<eventus::pipeline::FanOut>("test-fanout");

  std::vector<std::string> topics{"first-topic", "second-topic"};

  eventus::pipeline::TestContext ctx;
  using eventus::common::OperationArgument;
  for (auto& topic : topics) {
    auto node = MakeTestFilterNode(     //
        fmt::format("node-{}", topic),  //
        std::make_shared<eventus::filters::StringEqualFilter>(
            std::vector<OperationArgument>{{"src", "topic"},
                                           {"match_with", topic}}));
    auto sink = std::make_shared<eventus::pipeline::DebugSink>(
        fmt::format("log-sink-topic-{}", topic));
    sink->SetContext(ctx);
    node->LinkOutput(sink);
    fanout->AddOutput(node);
  }

  {
    auto filtered_node = MakeTestFilterNode(  //
        "node-otherwise-topics-log",          //
        std::make_shared<eventus::filters::StringArrayFilter>(
            std::vector<OperationArgument>{
                {"src", "topic"},
                {"policy", "contains_none"},
                {"match_with",
                 std::vector<std::string>(topics.begin(), topics.end())},
                {"value_type", "string"}}));

    auto sink =
        std::make_shared<eventus::pipeline::DebugSink>("log-sink-otherwise");
    sink->SetContext(ctx);
    filtered_node->LinkOutput(sink);
    fanout->AddOutput(filtered_node);
  }

  std::vector<std::string> cases{topics};
  cases.push_back("unknown-topic");
  eventus::pipeline::SeqNum seq_num{0};
  for (auto& topic : topics) {
    ctx.Reset();

    using eventus::pipeline::Event;
    using eventus::pipeline::PipelineItem;
    formats::json::ValueBuilder builder(formats::json::Type::kObject);
    builder["topic"] = topic;
    auto ejson = builder.ExtractValue();

    auto e = Event(ejson);
    PipelineItem item{seq_num++, Event{e}};
    fanout->Process(item);

    auto commited = ctx.Commited();
    ASSERT_EQ(commited.size(), topics.size() + 1);
  }
}
