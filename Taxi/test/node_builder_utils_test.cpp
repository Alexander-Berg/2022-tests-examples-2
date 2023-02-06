#include <eventus/operations/basic/filters/string_salt_filter/string_salt_filter.hpp>
#include <eventus/pipeline/node_builder_utils.hpp>
#include <eventus/pipeline/sink.hpp>
#include <eventus/pipeline/test_helpers.hpp>
#include <userver/utest/utest.hpp>

using namespace eventus::pipeline;
using namespace eventus::filters;

const std::string TST_VALUE_NAME = "tst_value";

TEST(PipelineOperation, OperationBreath) {
  TestContext ctx;

  auto mapper = UdfOperation::Make([](PipelineItem& msg, Output* out) {
    if (msg.seq_num == 1UL) msg.event->Set(TST_VALUE_NAME, 12);
    out->Push(msg);
  });
  auto sink = std::make_shared<DebugSink>("debug");
  sink->SetContext(ctx);
  auto p = MakeNode("1", std::move(mapper), MakeTestErrorHandler());
  auto p2 = MakeFilterNode(
      "2", [](const Event& ev) { return ev.HasKey(TST_VALUE_NAME); },
      ErrorHandler{MakeTestErrorHandler()});
  p->LinkOutput(p2);
  p2->LinkOutput(sink);

  auto item1 = ctx.MakeItem(1UL);
  auto item2 = ctx.MakeItem(2UL);
  p->Process(item1);
  p->Process(item2);

  ASSERT_EQ(2, ctx.Commited().size());
  ASSERT_EQ(2, sink->GetMessages().size());

  ASSERT_EQ(2UL, ctx.Commited()[1]);
  ASSERT_EQ(1UL, ctx.Commited()[0]);

  ASSERT_TRUE(sink->GetMessages()[0].event->HasKey(TST_VALUE_NAME));
  ASSERT_EQ((*sink->GetMessages()[0].event)
                .Get<formats::json::Value>(TST_VALUE_NAME)
                .As<int>(),
            12);
  ASSERT_FALSE(sink->GetMessages()[1].event);
}

TEST(PipelineOperation, FilterWrapper) {
  TestContext ctx;

  formats::json::ValueBuilder builder;
  builder[TST_VALUE_NAME] = "wheat";
  builder["key_to_int"] = 5318008;

  auto event = Event{builder.ExtractValue()};
  auto sink = std::make_shared<DebugSink>("debug");
  sink->SetContext(ctx);

  using eventus::common::OperationArgument;

  auto pepper_0_to_50 = std::make_shared<StringSaltFilter>(
      std::vector<OperationArgument>{{"src", TST_VALUE_NAME},
                                     {"salt", "pepper"},
                                     {"hash_from", static_cast<double>(0)},
                                     {"hash_to", static_cast<double>(50)}});
  auto pepper_50_to_100 = std::make_shared<StringSaltFilter>(
      std::vector<OperationArgument>{{"src", TST_VALUE_NAME},
                                     {"salt", "pepper"},
                                     {"hash_from", static_cast<double>(50)},
                                     {"hash_to", static_cast<double>(100)}});

  auto false_filter = MakeFilterNode(
      "1", CreateIsEventAcceptedFunc(pepper_0_to_50), MakeTestErrorHandler());
  false_filter->LinkOutput(sink);
  auto true_filter = MakeFilterNode(
      "1", CreateIsEventAcceptedFunc(pepper_50_to_100), MakeTestErrorHandler());
  true_filter->LinkOutput(sink);

  PipelineItem item1{1UL, event};
  false_filter->Process(item1);

  ASSERT_EQ(1, ctx.Commited().size());
  ASSERT_EQ(1, sink->GetMessages().size());

  ASSERT_FALSE(sink->GetMessages()[0].event);

  sink->Reset();
  PipelineItem item2{2UL, event};
  true_filter->Process(item2);

  ASSERT_EQ(2, ctx.Commited().size());
  ASSERT_EQ(1, sink->GetMessages().size());

  ASSERT_TRUE(sink->GetMessages()[0].event);
}

TEST(PipelineOperation, FilterList) {
  TestContext ctx;
  auto sink = std::make_shared<DebugSink>("debug");
  sink->SetContext(ctx);
  formats::json::ValueBuilder builder;
  builder[TST_VALUE_NAME] = "wheat";

  auto event1 = Event{builder.ExtractValue()};
  builder["key_to_int"] = 5318008;
  auto event2 = Event{builder.ExtractValue()};

  auto p = MakeFilterListNode(
      "2",
      {
          [](const Event& ev) { return ev.HasKey("46"); },
          [](const Event& ev) { return ev.HasKey(TST_VALUE_NAME); },
      },
      MakeTestErrorHandler());
  p->LinkOutput(sink);

  PipelineItem item1{1UL, event1};
  p->Process(item1);
  PipelineItem item2{2UL, event2};
  p->Process(item2);

  ASSERT_EQ(2, ctx.Commited().size());
  ASSERT_EQ(2, sink->GetMessages().size());

  ASSERT_TRUE(sink->GetMessages()[0].event);
  ASSERT_FALSE(sink->GetMessages()[1].event);
}

TEST(PipelineOperation, Switch) {
  formats::json::ValueBuilder builder;

  {
    // test the whole logic

    TestContext ctx;
    auto sink = std::make_shared<DebugSink>("debug");
    sink->SetContext(ctx);
    builder["42"] = "wheat";
    builder["43"] = "wheat";
    // should pass first and set key_1
    auto event1 = Event{builder.ExtractValue()};

    builder["47"] = "wheat";
    builder["42"] = "wheat";
    builder["44"] = "wheat";
    // should pass second and set key_2
    auto event2 = Event{builder.ExtractValue()};

    builder["47"] = "wheat";
    builder["42"] = "wheat";
    // should pass no one and has no key set
    auto event3 = Event{builder.ExtractValue()};

    auto p = MakeSwitchNode(
        "1",
        std::vector<SwitchOperation::SwitchOperationItem>{
            SwitchOperation::SwitchOperationItem{
                std::vector<FilterFunction>{
                    [](const Event& ev) { return ev.HasKey("42"); },
                    [](const Event& ev) { return ev.HasKey("43"); }},
                [](Event& event) { event.Set("key_1", 142); }

            },
            {{
                 [](const Event& ev) { return ev.HasKey("44"); },
             },
             [](Event& event) { event.Set("key_2", 143); }}

        },
        MakeTestErrorHandler());
    p->LinkOutput(sink);

    PipelineItem item1{1UL, event1};
    PipelineItem item2{2UL, event2};
    PipelineItem item3{3UL, event3};
    p->Process(item1);
    p->Process(item2);
    p->Process(item3);

    ASSERT_EQ(3, ctx.Commited().size());
    ASSERT_EQ(3, sink->GetMessages().size());

    ASSERT_TRUE(sink->GetMessages()[0].event);
    ASSERT_TRUE(sink->GetMessages()[1].event);
    ASSERT_TRUE(sink->GetMessages()[2].event);

    const auto& processed_1 = *(sink->GetMessages()[0].event);
    ASSERT_EQ(1UL, sink->GetMessages()[0].seq_num);
    ASSERT_TRUE(processed_1.HasKey("key_1"));
    ASSERT_FALSE(processed_1.HasKey("key_2"));
    ASSERT_TRUE(processed_1.HasKey("42"));

    const auto& processed_2 = *(sink->GetMessages()[1].event);
    ASSERT_EQ(2UL, sink->GetMessages()[1].seq_num);
    ASSERT_TRUE(processed_2.HasKey("key_2"));
    ASSERT_FALSE(processed_2.HasKey("key_1"));
    ASSERT_TRUE(processed_2.HasKey("44"));

    const auto& processed_3 = *(sink->GetMessages()[2].event);
    ASSERT_EQ(3UL, sink->GetMessages()[2].seq_num);
    ASSERT_FALSE(processed_3.HasKey("key_2"));
    ASSERT_FALSE(processed_3.HasKey("key_1"));
  }

  {
    // test empty filters

    TestContext ctx;
    auto sink = std::make_shared<DebugSink>("debug");
    sink->SetContext(ctx);
    builder["43"] = "wheat";
    // should pass second and set key_2
    auto event1 = Event{builder.ExtractValue()};

    auto p =
        MakeSwitchNode("1",
                       std::vector<SwitchOperation::SwitchOperationItem>{
                           SwitchOperation::SwitchOperationItem{
                               std::vector<FilterFunction>{[](const Event& ev) {
                                 return ev.HasKey("42");
                               }},
                               [](Event& event) { event.Set("key_1", 142); }},
                           {{}, [](Event& event) { event.Set("key_2", 143); }}},
                       MakeTestErrorHandler());
    p->LinkOutput(sink);

    PipelineItem item1{1UL, event1};
    p->Process(item1);

    ASSERT_EQ(1, ctx.Commited().size());
    ASSERT_EQ(1, sink->GetMessages().size());

    ASSERT_TRUE(sink->GetMessages()[0].event);

    const auto& processed_1 = *(sink->GetMessages()[0].event);
    ASSERT_EQ(1UL, sink->GetMessages()[0].seq_num);
    ASSERT_TRUE(processed_1.HasKey("key_2"));
    ASSERT_FALSE(processed_1.HasKey("key_1"));
    ASSERT_TRUE(processed_1.HasKey("43"));
  }
}
