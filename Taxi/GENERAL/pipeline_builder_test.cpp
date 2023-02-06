#include <fmt/format.h>

#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include <eventus/pipeline/pipeline_builder.hpp>
#include <eventus/pipeline/sink.hpp>
#include <eventus/pipeline/test_helpers.hpp>
#include <eventus/sinks/sink_factory.hpp>
#include <eventus/sources/source_manager.hpp>

namespace {

using SourcesMap =
    std::unordered_map<std::string, eventus::pipeline::SourceUPtr>;

class InvalidFilter : public std::exception {
  std::string msg;

 public:
  InvalidFilter(std::string name)
      : msg{fmt::format("Invalid filter: {}", name)} {}

  const char* what() const noexcept override { return msg.c_str(); }
};

class InvalidSink : public std::exception {
  std::string msg;

 public:
  InvalidSink(std::string name) : msg{fmt::format("Invalid sink: {}", name)} {}

  const char* what() const noexcept override { return msg.c_str(); }
};

struct TestStat {
  std::unordered_map<std::string, size_t> sink_usage{};
  std::unordered_map<std::string, size_t> empty_message_at{};
  std::unordered_map<std::string, size_t> has_message_at{};
};

class TestNamedSink : public eventus::pipeline::Sink {
 public:
  std::shared_ptr<TestStat> stat;

  TestNamedSink(const std::string& name, std::shared_ptr<TestStat> stat)
      : Sink(name), stat{std::move(stat)} {}

  void Process(eventus::pipeline::PipelineItem& msg) override {
    stat->sink_usage[GetName()]++;
    stat->empty_message_at[GetName()] +=
        static_cast<size_t>(!msg.event.has_value());
    stat->has_message_at[GetName()] +=
        static_cast<size_t>(msg.event.has_value());
    GetContext().GetPipelineStateManager().Commit(msg.seq_num);
  };
};

class TestOperationFactory : public eventus::pipeline::OperationFactory {
 public:
  TestOperationFactory() {}
  virtual ~TestOperationFactory() {}

  eventus::pipeline::FilterFunction MakeFilter(
      const std::string& name,
      const eventus::common::OperationArgs& /*arguments*/) const override {
    using eventus::pipeline::Event;
    if (name == "pass") {
      LOG_DEBUG() << "Making filter 'pass'";
      return [](const Event& /*event*/) { return true; };
    }
    if (name == "reject") {
      LOG_DEBUG() << "Making filter 'reject'";
      return [](const Event& /*event*/) { return false; };
    }
    throw InvalidFilter(name);
  }

  eventus::pipeline::MapperFunction MakeMapper(
      const std::string& name,
      const eventus::common::OperationArgs& /*arguments*/) const override {
    using eventus::pipeline::Event;
    LOG_DEBUG() << "Making mapper '" << name << "'";
    return [](Event&) {};
  }

  eventus::pipeline::OperationPtr MakeCustom(
      const std::string& /*name*/,
      const eventus::common::OperationArgs& /*arguments*/) const override {
    return nullptr;
  }
};

class TestSinkFactory final : public eventus::sinks::SinkFactory {
 public:
  std::shared_ptr<TestStat> stat;
  TestSinkFactory(std::shared_ptr<TestStat> stat) : stat{std::move(stat)} {}

  std::unordered_set<std::string> GetAvailableSinkNames() const override {
    return {"named-sink", "second-sink"};
  };

 private:
  eventus::pipeline::SinkPtr MakeSinkImpl(
      const std::string& sink_name,
      const eventus::common::OperationArgs&) const override {
    if (sink_name == "named-sink") {
      return std::make_shared<TestNamedSink>(sink_name, stat);
    }
    throw InvalidSink{sink_name};
  }
};

std::shared_ptr<eventus::sources::SourceManager> MakeTestSourceManager() {
  SourcesMap sources;
  sources["test-source"] =
      std::make_unique<eventus::pipeline::impl::TestSource>("test-source");
  return std::make_shared<eventus::sources::SourceManager>(std::move(sources));
}

std::shared_ptr<eventus::pipeline::config::Pipeline> MakePipelineCfg(
    size_t nodes_count) {
  using namespace eventus::pipeline;
  using namespace std::string_literals;

  auto pipeline_cfg = std::make_shared<config::Pipeline>(
      "test-pipeline", false, config::Source("test-source"s),
      eventus::pipeline::config::OutputVariant{}, 1);

  config::FanOut fanout;

  for (size_t n = 0; n < nodes_count; n++) {
    config::OperationNode node;
    node.name = fmt::format("node-{}", n);
    node.disabled = false;
    node.operation = config::OperationVariant();
    node.output = config::OutputVariant(config::Sink("named-sink"s, {}));
    node.error_policy = std::nullopt;
    fanout.outputs.emplace_back(config::OutputVariant(std::move(node)));
  }

  pipeline_cfg->entry_point = config::OutputVariant(std::move(fanout));
  return pipeline_cfg;
}

}  // namespace

UTEST(PipelineSuite, BuilderTest) {
  using namespace eventus::pipeline;
  using namespace std::string_literals;

  auto stat = std::make_shared<TestStat>();

  auto operation_factory = std::make_shared<TestOperationFactory>();
  auto source_manager = MakeTestSourceManager();
  auto sink_factory = std::make_shared<TestSinkFactory>(stat);

  eventus::statistics::PipelineStatisticsPtr pipeline_stats =
      std::make_shared<eventus::statistics::PipelineStatistics>();

  const auto branch_count = 2;
  auto pipeline_cfg = MakePipelineCfg(branch_count);

  pipeline_cfg->entry_point.fanout->outputs[0].output->operation =
      config::OperationVariant(
          config::Operation("pass"s, config::OperationType::kFilter, {}));

  pipeline_cfg->entry_point.fanout->outputs[1].output->operation =
      config::OperationVariant(
          config::Operation("reject"s, config::OperationType::kFilter, {}));

  const auto& default_config = dynamic_config::GetDefaultSnapshot();

  eventus::pipeline::PipelineBuilder builder(pipeline_cfg, operation_factory,
                                             source_manager, sink_factory,
                                             pipeline_stats, default_config);

  auto pipeline = builder.FinalizePipeline();
  ASSERT_NE(pipeline, nullptr);

  ASSERT_EQ(builder.GetUsedSinksCount(), branch_count);
  ASSERT_EQ(builder.GetUsedSinkNames(),
            std::unordered_set<std::string>{"named-sink"});

  PipelineTestHelper pipeline_helper{pipeline};
  {
    eventus::pipeline::Event event({});
    PipelineItem item{1, event};
    pipeline_helper.ProcessItem(std::move(item));
    ASSERT_EQ(stat->sink_usage.size(), 1);
    ASSERT_EQ(stat->sink_usage["named-sink"], 2);
    ASSERT_EQ(stat->empty_message_at["named-sink"], 1);
    ASSERT_EQ(stat->has_message_at["named-sink"], 1);
  }
}

UTEST(PipelineSuite, BuilderNoOperationTest) {
  using namespace eventus::pipeline;
  using namespace std::string_literals;

  auto stat = std::make_shared<TestStat>();

  auto operation_factory = std::make_shared<TestOperationFactory>();
  auto source_manager = MakeTestSourceManager();
  auto sink_factory = std::make_shared<TestSinkFactory>(stat);

  eventus::statistics::PipelineStatisticsPtr pipeline_stats =
      std::make_shared<eventus::statistics::PipelineStatistics>();

  auto pipeline_cfg = MakePipelineCfg(1);

  const auto& default_config = dynamic_config::GetDefaultSnapshot();

  // Due to no operation is set but node is enabled
  EXPECT_THROW(eventus::pipeline::PipelineBuilder(
                   pipeline_cfg, operation_factory, source_manager,
                   sink_factory, pipeline_stats, default_config),
               std::exception);
}

UTEST(PipelineSuite, BuilderDisabledOperationTest) {
  using namespace eventus::pipeline;
  using namespace std::string_literals;

  auto stat = std::make_shared<TestStat>();

  auto operation_factory = std::make_shared<TestOperationFactory>();
  auto source_manager = MakeTestSourceManager();
  auto sink_factory = std::make_shared<TestSinkFactory>(stat);

  eventus::statistics::PipelineStatisticsPtr pipeline_stats =
      std::make_shared<eventus::statistics::PipelineStatistics>();

  auto pipeline_cfg = MakePipelineCfg(1);

  pipeline_cfg->entry_point.fanout->outputs[0].output->disabled = true;

  const auto& default_config = dynamic_config::GetDefaultSnapshot();

  eventus::pipeline::PipelineBuilder builder(pipeline_cfg, operation_factory,
                                             source_manager, sink_factory,
                                             pipeline_stats, default_config);

  auto pipeline = builder.FinalizePipeline();
  ASSERT_NE(pipeline, nullptr);

  PipelineTestHelper pipeline_helper{pipeline};
  {
    eventus::pipeline::Event event({});
    PipelineItem item{1, event};
    pipeline_helper.ProcessItem(std::move(item));
    ASSERT_EQ(stat->sink_usage.size(), 1);
    ASSERT_EQ(stat->sink_usage["named-sink"], 1);
    ASSERT_EQ(stat->empty_message_at["named-sink"], 0);
    ASSERT_EQ(stat->has_message_at["named-sink"], 1);
  }
}
