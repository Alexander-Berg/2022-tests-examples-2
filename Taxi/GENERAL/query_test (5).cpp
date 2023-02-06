#include <yt-replica-reader/query.hpp>

#include <functional>

#include <userver/utest/utest.hpp>

namespace yt_replica_reader {
namespace {

models::YtTargetInfo MakeTarget(std::string table,
                                std::vector<std::string> parts,
                                bool is_runtime) {
  return models::YtTargetInfo::MakeYtTargetInfo(
      table,
      is_runtime ? models::ClusterType::kRuntime
                 : models::ClusterType::kMapReduce,
      parts);
}

models::YtTargetsInfoPtr MakeTargets() {
  auto targets = std::make_shared<models::YtTargetsInfo>();
  targets->emplace("target-1-rt", MakeTarget("path-1", {}, true));
  targets->emplace("target-2-rt", MakeTarget("path-2", {}, true));
  targets->emplace("target-3-mr", MakeTarget("path-3", {}, false));
  targets->emplace("target-4-rt-part",
                   MakeTarget("path-4", {"part-1", "part-2"}, true));
  targets->emplace("target-5-rt-part",
                   MakeTarget("path-5", {"part-1", "part-2"}, true));
  return targets;
}

}  // namespace

class QueryBuilderTester {
 public:
  QueryBuilderTester(std::string format)
      : builder_(MakeTargets(), std::move(format)) {}

  QueryBuilderTester& FormatTable(std::string value) {
    builder_.FormatTable(std::move(value));
    return *this;
  }

  template <typename T>
  QueryBuilderTester& Format(T value) {
    builder_.Format(std::move(value));
    return *this;
  }

  std::vector<std::string> GetQueries() const { return builder_.GetQueries(); }
  std::optional<models::ClusterType> GetClustersType() const {
    return builder_.GetClustersType();
  }
  std::vector<std::string> GetTargetNames() const {
    return builder_.GetTargetNames();
  }

 private:
  Query builder_;
};

struct TestArgs {
  std::function<QueryBuilderTester()> query_builder;
  bool expect_throw;
  std::vector<std::string> expected_queries;
  std::vector<std::string> expected_targets;
  std::optional<models::ClusterType> expected_type;

  TestArgs(std::function<QueryBuilderTester()> builder, bool expect_throw,
           std::vector<std::string> queries = {},
           std::vector<std::string> targets = {},
           std::optional<models::ClusterType> type = models::ClusterType::kBoth)
      : query_builder(std::move(builder)),
        expect_throw(expect_throw),
        expected_queries(std::move(queries)),
        expected_targets(std::move(targets)),
        expected_type(std::move(type)) {}
};

class TestQueryBuilder : public ::testing::TestWithParam<TestArgs> {};

TEST_P(TestQueryBuilder, Tests) {
  auto args = GetParam();
  if (args.expect_throw) {
    ASSERT_THROW((args.query_builder)(), std::runtime_error);
  } else {
    auto query = (args.query_builder)();
    ASSERT_EQ(args.expected_targets, query.GetTargetNames());
    ASSERT_EQ(args.expected_queries, query.GetQueries());
    if (args.expected_type && query.GetClustersType()) {
      ASSERT_EQ(args.expected_type, query.GetClustersType());
    } else {
      ASSERT_FALSE(args.expected_type || query.GetClustersType());
    }
  }
}

INSTANTIATE_TEST_SUITE_P(
    QueryBuilder, TestQueryBuilder,
    ::testing::Values(
        // Check RT table
        TestArgs{
            [] {
              return QueryBuilderTester("* FROM %1%")
                  .FormatTable("target-1-rt");
            },
            false,
            {"* FROM [path-1]"},
            {"target-1-rt"},
            models::ClusterType::kRuntime,
        },
        // Check MR table
        TestArgs{
            [] {
              return QueryBuilderTester("* FROM %1%")
                  .FormatTable("target-3-mr");
            },
            false,
            {"* FROM [path-3]"},
            {"target-3-mr"},
            models::ClusterType::kMapReduce,
        },
        // Check table with partitions
        TestArgs{
            [] {
              return QueryBuilderTester("* FROM %1%")
                  .FormatTable("target-4-rt-part");
            },
            false,
            {"* FROM [path-4/part-1]", "* FROM [path-4/part-2]"},
            {"target-4-rt-part"},
            models::ClusterType::kRuntime,
        },
        // Check tables with join
        TestArgs{
            [] {
              return QueryBuilderTester("* FROM %1% JOIN %2%")
                  .FormatTable("target-1-rt")
                  .FormatTable("target-2-rt");
            },
            false,
            {"* FROM [path-1] JOIN [path-2]"},
            {"target-1-rt", "target-2-rt"},
            models::ClusterType::kRuntime,
        },
        // Check tables with partitions with join
        TestArgs{
            [] {
              return QueryBuilderTester("* FROM %1% JOIN %2%")
                  .FormatTable("target-1-rt")
                  .FormatTable("target-4-rt-part");
            },
            false,
            {"* FROM [path-1] JOIN [path-4/part-1]",
             "* FROM [path-1] JOIN [path-4/part-2]"},
            {"target-1-rt", "target-4-rt-part"},
            models::ClusterType::kRuntime,
        },
        // Check RT and MR targets in query
        TestArgs{
            [] {
              return QueryBuilderTester("* FROM %1% JOIN %2%")
                  .FormatTable("target-1-rt")
                  .FormatTable("target-3-mr");
            },
            false,
            {"* FROM [path-1] JOIN [path-3]"},
            {"target-1-rt", "target-3-mr"},
            std::nullopt,
        },
        // ERROR: Undefined target name
        TestArgs{
            [] {
              return QueryBuilderTester("* FROM %1%").FormatTable("undefined");
            },
            true,
        },
        // ERROR: Multiple tables with partitions
        TestArgs{
            [] {
              return QueryBuilderTester("* FROM %1% JOIN %2%")
                  .FormatTable("target-4-rt-part")
                  .FormatTable("target-5-rt-part");
            },
            true,
        },
        // Check bool arg
        TestArgs{
            [] { return QueryBuilderTester("%1%").Format(true); },
            false,
            {"true"},
        },
        // Check integer arg
        TestArgs{
            [] { return QueryBuilderTester("%1%").Format(1); },
            false,
            {"1"},
        },
        // Check double arg
        TestArgs{
            [] { return QueryBuilderTester("%1%").Format(.123); },
            false,
            {"0.12300"},
        },
        // Check double arg
        TestArgs{
            [] { return QueryBuilderTester("%1%").Format(10000.23456); },
            false,
            {"10000.23456"},
        },
        // Check string arg
        TestArgs{
            [] {
              return QueryBuilderTester("%1%").Format(
                  std::string("xxx\n\r\t\"\\xxx"));
            },
            false,
            {"\"xxx\\n\\r\\t\\\"\\\\xxx\""},
        },
        // Check empty vector arg
        TestArgs{
            [] {
              return QueryBuilderTester("%1%").Format(
                  std::vector<std::string>{});
            },
            false,
            {"()"},
        },
        // Check vector int arg
        TestArgs{
            [] {
              return QueryBuilderTester("%1%").Format(
                  std::vector<int>{1, 2, 3, 4, 5});
            },
            false,
            {"(1, 2, 3, 4, 5)"},
        },
        // Check vector string arg
        TestArgs{
            [] {
              return QueryBuilderTester("%1%").Format(
                  std::vector<std::string>{"1", "2", "3", "xxx\n\r\t\"\\xxx"});
            },
            false,
            {"(\"1\", \"2\", \"3\", \"xxx\\n\\r\\t\\\"\\\\xxx\")"},
        }));

}  // namespace yt_replica_reader
