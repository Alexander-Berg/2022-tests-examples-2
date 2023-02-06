#include <userver/utest/utest.hpp>

#include <eventus/pipeline/config/error_handler.hpp>
#include <eventus/pipeline/node_builder_utils.hpp>
#include <eventus/pipeline/sink.hpp>
#include <eventus/pipeline/test_helpers.hpp>

using namespace eventus::pipeline;

const std::string TST_VALUE_NAME = "tst_value";

TEST(Pipeline, NodeBreath) {
  TestContext ctx;
  auto mapper = [](PipelineItem& msg, Output* out) {
    msg.event->Set(TST_VALUE_NAME, 12);
    out->Push(msg);
  };
  auto p = eventus::pipeline::PipelineNode(
      "tmp", UdfOperation::Make(mapper), MakeTestErrorHandler(),
      std::make_shared<eventus::statistics::NodeStatistics>());

  auto sink = std::make_shared<DebugSink>("debug");
  sink->SetContext(ctx);
  p.LinkOutput(sink);

  auto item = ctx.MakeItem(1UL);
  p.SetDisabled(true);
  p.Process(item);
  ASSERT_FALSE(ctx.Commited().empty());
  ASSERT_FALSE(sink->GetMessages()[0].event->HasKey(TST_VALUE_NAME));

  p.SetDisabled(false);
  p.Process(item);
  auto empty_msg = ctx.MakeItem(2UL);
  empty_msg.event.reset();
  p.Process(empty_msg);
  ASSERT_EQ(3, ctx.Commited().size());
  ASSERT_EQ(3, sink->GetMessages().size());

  ASSERT_EQ(2UL, ctx.Commited()[2]);
  ASSERT_EQ(1UL, ctx.Commited()[1]);

  ASSERT_TRUE(sink->GetMessages()[1].event->HasKey(TST_VALUE_NAME));
  ASSERT_EQ((*sink->GetMessages()[1].event)
                .Get<formats::json::Value>(TST_VALUE_NAME)
                .As<int>(),
            12);
}

UTEST(Pipeline, NodeErrorHandling) {
  TestContext ctx;
  int attempt = 0;
  auto mapper = [&attempt](Event& event) {
    if (attempt++ < 3) {
      throw std::logic_error("ouch");
    }
    event.Set("abacaba", "dabacaba");
  };
  const auto attempts_limit = 4;
  auto p = eventus::pipeline::PipelineNode(
      "tmp", MapperOperation::Make(mapper),
      ErrorHandler(ErrorHandlingPolicy{
          attempts_limit, std::chrono::milliseconds{0},
          std::chrono::milliseconds{10000}, 1,
          eventus::pipeline::config::ActionAfterErroneousExecution::kPropagate,
          eventus::pipeline::config::ErroneousStatisticsLevel::kError}),
      std::make_shared<eventus::statistics::NodeStatistics>());

  auto sink = std::make_shared<DebugSink>("debug");
  sink->SetContext(ctx);
  p.LinkOutput(sink);

  auto item = ctx.MakeItem(1UL);
  p.Process(item);

  ASSERT_EQ(sink->GetMessages()[0].event->Get<std::string>("abacaba"),
            "dabacaba");
  ASSERT_EQ(attempt, 4);

  attempt = -5;
  item = ctx.MakeItem(1UL);
  p.Process(item);
  ASSERT_FALSE(sink->GetMessages()[1].event->HasKey("abacaba"));
  ASSERT_EQ(attempt, -5 + attempts_limit);
}
