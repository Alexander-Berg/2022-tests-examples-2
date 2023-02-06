#include <eventus/sources/logbroker_source/parser_json.hpp>

#include <userver/utest/utest.hpp>

#include <benchmark/benchmark_utils.hpp>
#include <eventus/pipeline/test_helpers.hpp>

void TestParser(int number_of_threads, int number_of_messages) {
  eventus::sources::logbroker_source::ParserJson parser(number_of_threads);

  std::string data;
  for (int i = 0; i < number_of_messages; i++) {
    data += benchmark_utils::GenerateJson(1 << 11, i) + "\n\n";
  }
  data.pop_back();

  std::vector<eventus::pipeline::PipelineItem> items;
  items.push_back({});
  ASSERT_TRUE(parser.ParseItems(items, data));

  ASSERT_EQ(items.size(), number_of_messages + 1);
  for (int i = 0; i < number_of_messages; i++) {
    ASSERT_EQ(
        items[i + 1].event->GetData(),
        formats::json::FromString(benchmark_utils::GenerateJson(1 << 11, i)));
  }
}

UTEST(LogbrokerCommitCoordinator, test_commit_once) {
  for (int thr = 1; thr < 10; thr++) {
    for (int msgs = 20; msgs < 100; msgs += 7) {
      TestParser(thr, msgs);
    }
  }
}
