#include <userver/dump/test_helpers.hpp>
#include <userver/utest/utest.hpp>

#include <yt-replica-reader/models/targets_info.hpp>

TEST(ReplicationYtTargetsCache, Serialization) {
  using yt_replica_reader::models::ClusterType;
  using yt_replica_reader::models::YtTargetInfo;

  auto info = YtTargetInfo::MakeYtTargetInfo(
      "/tmp/some_table", ClusterType::kMapReduce, {"2020", "2021"});
  info.AddYtCluster("arnold", std::chrono::system_clock::now());

  const auto restored = dump::FromBinary<YtTargetInfo>(dump::ToBinary(info));

  EXPECT_EQ(restored.full_table_path, info.full_table_path);
  EXPECT_EQ(restored.partitions, info.partitions);
  EXPECT_EQ(restored.clusters_delay, info.clusters_delay);
  EXPECT_EQ(restored.clusters_last_replicated, info.clusters_last_replicated);
  EXPECT_EQ(restored.max_last_replicated, info.max_last_replicated);
  EXPECT_EQ(restored.cluster_type, info.cluster_type);
}
