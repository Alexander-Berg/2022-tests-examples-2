#include <gtest/gtest.h>

#include <utils/except.hpp>
#include <utils/link_builder.hpp>

#include "tools/testutils.hpp"

namespace hejmdal::utils {

const auto MockTime = testutils::MockTime;

time::TimeRange MockTimeRange(std::time_t begin, std::time_t end) {
  auto begin_time = MockTime(begin);
  auto end_time = MockTime(end);
  return time::TimeRange(begin_time, end_time);
}

TEST(TestLinkBuilder, YasmDatabaseMetricsDashboard) {
  // 1. Unsupported types
  // Nanny
  ASSERT_THROW(auto _ = LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                   models::ClusterType::kNanny, "test_cluster_id",
                   "test_dbname", "test_shard", std::nullopt),
               except::Error);

  // Conductor
  ASSERT_THROW(auto _ = LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                   models::ClusterType::kConductor, "test_cluster_id",
                   "test_dbname", "test_shard", std::nullopt),
               except::Error);

  // Mongo Lxc
  ASSERT_THROW(auto _ = LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                   models::ClusterType::kMongoLxc, "test_cluster_id",
                   "test_dbname", "test_shard", std::nullopt),
               except::Error);

  // Redis Lxc
  ASSERT_THROW(auto _ = LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                   models::ClusterType::kRedisLxc, "test_cluster_id",
                   "test_dbname", "test_shard", std::nullopt),
               except::Error);

  // 2. Supported types
  // Postgres
  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kPostgres, "test_cluster_id",
                "test_dbname", "test_shard", std::nullopt),
            "https://yasm.yandex-team.ru/template/panel/dbaas_postgres_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kPostgres, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kCpu),
            "https://yasm.yandex-team.ru/template/panel/dbaas_postgres_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/cpu/?by=hosts");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kPostgres, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kRam),
            "https://yasm.yandex-team.ru/template/panel/dbaas_postgres_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/mem/?by=hosts");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kPostgres, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kDisk),
            "https://yasm.yandex-team.ru/template/panel/dbaas_postgres_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/size/?by=hosts");

  // Mongo Mdb
  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kMongoMdb, "test_cluster_id",
                "test_dbname", "test_shard", std::nullopt),
            "https://yasm.yandex-team.ru/template/panel/dbaas_mongodb_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kMongoMdb, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kCpu),
            "https://yasm.yandex-team.ru/template/panel/dbaas_mongodb_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/cpu/?by=hosts");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kMongoMdb, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kRam),
            "https://yasm.yandex-team.ru/template/panel/dbaas_mongodb_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/mem/?by=hosts");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kMongoMdb, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kDisk),
            "https://yasm.yandex-team.ru/template/panel/dbaas_mongodb_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/size/?by=hosts");

  // Redis Mdb
  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kRedisMdb, "test_cluster_id",
                "test_dbname", "test_shard", std::nullopt),
            "https://yasm.yandex-team.ru/template/panel/dbaas_redis_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kRedisMdb, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kCpu),
            "https://yasm.yandex-team.ru/template/panel/dbaas_redis_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/cpu/?by=hosts");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kRedisMdb, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kRam),
            "https://yasm.yandex-team.ru/template/panel/dbaas_redis_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/mem/?by=hosts");

  ASSERT_EQ(LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                models::ClusterType::kRedisMdb, "test_cluster_id",
                "test_dbname", "test_shard", models::ResourceType::kDisk),
            "https://yasm.yandex-team.ru/template/panel/dbaas_redis_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/disksize/"
            "?by=hosts");
}

TEST(TestLinkBuilder, YasmDatabaseMetricsDashboardWithTimeRange) {
  // With resource
  const auto link1 =
      models::Link{"test text",
                   LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                       models::ClusterType::kPostgres, "test_cluster_id",
                       "test_dbname", "test_shard", models::ResourceType::kCpu),
                   models::LinkType::kYasmDbResourcesDashboard};

  ASSERT_EQ(LinkBuilder::BuildGraphWithTimeRange(MockTimeRange(1, 3), link1),
            "https://yasm.yandex-team.ru/template/panel/dbaas_postgres_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/cpu/?by=hosts&"
            "from=1000&to=3000");

  // Without resource
  const auto link2 =
      models::Link{"test text",
                   LinkBuilder::BuildToYasmDatabaseMetricsDashboard(
                       models::ClusterType::kPostgres, "test_cluster_id",
                       "test_dbname", "test_shard", std::nullopt),
                   models::LinkType::kYasmDbResourcesDashboard};

  ASSERT_EQ(LinkBuilder::BuildGraphWithTimeRange(MockTimeRange(1, 3), link2),
            "https://yasm.yandex-team.ru/template/panel/dbaas_postgres_metrics/"
            "cid=test_cluster_id;dbname=test_dbname.test_shard/?"
            "from=1000&to=3000");
}

TEST(TestLinkBuilder, SolomonMDBDatabaseMetricsDashboard) {
  // 1. Unsupported types
  // Nanny
  ASSERT_THROW(auto _ = LinkBuilder::BuildToSolomonMDBDatabaseMetricsDashboard(
                   models::ClusterType::kNanny, "test_cluster_id"),
               except::Error);

  // Conductor
  ASSERT_THROW(auto _ = LinkBuilder::BuildToSolomonMDBDatabaseMetricsDashboard(
                   models::ClusterType::kConductor, "test_cluster_id"),
               except::Error);

  // Mongo Lxc
  ASSERT_THROW(auto _ = LinkBuilder::BuildToSolomonMDBDatabaseMetricsDashboard(
                   models::ClusterType::kMongoLxc, "test_cluster_id"),
               except::Error);

  // Redis Lxc
  ASSERT_THROW(auto _ = LinkBuilder::BuildToSolomonMDBDatabaseMetricsDashboard(
                   models::ClusterType::kRedisLxc, "test_cluster_id"),
               except::Error);

  // 2. Supported types
  // Postgres
  ASSERT_EQ(
      LinkBuilder::BuildToSolomonMDBDatabaseMetricsDashboard(
          models::ClusterType::kPostgres, "test_cluster_id"),
      "https://solomon.yandex-team.ru/?project=internal-mdb&cluster=mdb_"
      "test_cluster_id&service=mdb&dashboard=internal-mdb-cluster-postgres");

  // Mongo Mdb
  ASSERT_EQ(
      LinkBuilder::BuildToSolomonMDBDatabaseMetricsDashboard(
          models::ClusterType::kMongoMdb, "test_cluster_id"),
      "https://solomon.yandex-team.ru/?project=internal-mdb&cluster=mdb_"
      "test_cluster_id&service=mdb&dashboard=internal-mdb-cluster-mongodb");

  // Redis Mdb
  ASSERT_EQ(LinkBuilder::BuildToSolomonMDBDatabaseMetricsDashboard(
                models::ClusterType::kRedisMdb, "test_cluster_id"),
            "https://solomon.yandex-team.ru/?project=internal-mdb&cluster=mdb_"
            "test_cluster_id&service=mdb&dashboard=internal-mdb-cluster-redis");
}

}  // namespace hejmdal::utils
