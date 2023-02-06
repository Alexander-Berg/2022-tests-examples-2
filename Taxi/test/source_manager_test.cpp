#include <userver/engine/task/task_with_result.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <eventus/pipeline/source.hpp>
#include <eventus/pipeline/test_helpers.hpp>
#include <eventus/sources/source_manager.hpp>

#include <fmt/format.h>

namespace {

using SourcesMap =
    std::unordered_map<std::string, eventus::pipeline::SourceUPtr>;

eventus::pipeline::SourceUPtr MakeTestSource(const std::string& name) {
  return std::make_unique<eventus::pipeline::impl::TestSource>(name);
}

SourcesMap MakeTestSources(size_t sources_count = 1) {
  SourcesMap sources;
  for (size_t n = 0; n < sources_count; n++) {
    auto name = fmt::format("test-source-{}", n);
    sources[name] = MakeTestSource(name);
  }
  return sources;
}

}  // namespace

TEST(SourceSuite, BadSourceTest) {
  SourcesMap sources;
  sources["test-source"] = nullptr;
  EXPECT_THROW(
      std::make_shared<eventus::sources::SourceManager>(std::move(sources)),
      std::exception);
}

UTEST(SourceSuite, Test) {
  static const auto kSourceName = "test-source";
  static const auto kPipelineName = "pipelines-name";
  SourcesMap sources;
  auto source =
      std::make_unique<eventus::pipeline::impl::TestSource>(kSourceName);
  auto source_stats = source->stats;
  sources[kSourceName] = std::move(source);

  auto source_manager =
      std::make_shared<eventus::sources::SourceManager>(std::move(sources));

  std::vector<eventus::pipeline::PipelineItem> bulk;

  for (int call_times = 1; call_times <= 2; call_times++) {
    {
      auto source = source_manager->Acquire(kSourceName, kPipelineName);
      ASSERT_NE(source, nullptr);
      ASSERT_EQ(source_manager->GetSourceOwner(kSourceName),
                std::optional<std::string>{kPipelineName});
      EXPECT_THROW(source_manager->Acquire(kSourceName, kPipelineName),
                   eventus::sources::SourceAcqisitionFailureException);

      source->PopNoBlock(bulk, {});
      ASSERT_EQ(source_stats->pop_noblock_called_times, call_times);
      source->Pop(bulk);
      ASSERT_EQ(source_stats->pop_called_times, call_times);
      source->Commit(1);
      ASSERT_EQ(source_stats->commit_called_times, call_times);
    }
    ASSERT_EQ(source_manager->GetSourceOwner(kSourceName),
              std::optional<std::string>{});
  };
}

UTEST_MT(SourceSuite, ReleaseRaceTest, 3) {
  const auto kSourcesCount = 1000;
  auto source_manager = std::make_shared<eventus::sources::SourceManager>(
      MakeTestSources(kSourcesCount));

  for (int repeat = 0; repeat < 10; repeat++) {
    std::vector<eventus::pipeline::SourceUPtr> sources;
    for (int n = 0; n < kSourcesCount; n++) {
      auto source = source_manager->Acquire(fmt::format("test-source-{}", n),
                                            fmt::format("pipeline-name-{}", n));
      ASSERT_NE(source, nullptr);
      sources.emplace_back(std::move(source));
    }

    std::vector<engine::TaskWithResult<void>> tasks;
    for (int n = 0; n < kSourcesCount; n++) {
      tasks.push_back(utils::Async(
          "release-task", [& source = sources[n]] { source.reset(); }));
    }

    for (auto& task : tasks) {
      EXPECT_NO_THROW(task.Get());
    }
  }
}
