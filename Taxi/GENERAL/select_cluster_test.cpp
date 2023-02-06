#include <unordered_set>

#include <yt-replica-reader/models/targets_info.hpp>
#include <yt-replica-reader/query.hpp>

#include <userver/utest/utest.hpp>

#include "select_cluster.hpp"

namespace yt_replica_reader {
using ClustersSet = std::unordered_set<std::string>;

std::chrono::system_clock::time_point Timepoint(int seconds) {
  return std::chrono::system_clock::now() + std::chrono::seconds(seconds);
}

const std::string kTargetName = "test_target";
models::YtTargetsInfoPtr MakeTargets(models::YtTargetInfo target_info) {
  models::YtTargetsInfo targets_info{{kTargetName, target_info}};
  return std::make_shared<models::YtTargetsInfo>(targets_info);
}

TEST(TestGetAvailableClusters, TestClustersArgs) {
  {
    models::YtTargetInfo target_info;
    target_info.AddYtCluster("hahn", Timepoint(1000));
    target_info.AddYtCluster("arni", Timepoint(900));
    target_info.AddYtCluster("zeno", Timepoint(600));
    auto clusters = yt_replica_reader::models::GetAvailableClusters(
        MakeTargets(target_info), kTargetName, std::nullopt);
    EXPECT_EQ(ClustersSet({"hahn", "arni", "zeno"}), clusters);
  }

  {
    models::YtTargetInfo target_info;
    target_info.AddYtCluster("hahn", Timepoint(1000));
    target_info.AddYtCluster("arni", Timepoint(900));
    target_info.AddYtCluster("zeno", Timepoint(600));
    auto clusters = yt_replica_reader::models::GetAvailableClusters(
        MakeTargets(target_info), kTargetName, 200);
    EXPECT_EQ(ClustersSet({"hahn", "arni"}), clusters);
  }

  {
    models::YtTargetInfo target_info;
    target_info.AddYtCluster("hahn", Timepoint(1000));
    target_info.AddYtCluster("arni", Timepoint(900));
    target_info.AddYtCluster("zeno", std::nullopt);
    auto clusters = yt_replica_reader::models::GetAvailableClusters(
        MakeTargets(target_info), kTargetName, 200);
    EXPECT_EQ(ClustersSet({"hahn", "arni"}), clusters);
  }

  {
    models::YtTargetInfo target_info;
    target_info.AddYtCluster("hahn", Timepoint(1000));
    target_info.AddYtCluster("arni", std::nullopt);
    target_info.AddYtCluster("zeno", std::nullopt);
    auto clusters = yt_replica_reader::models::GetAvailableClusters(
        MakeTargets(target_info), kTargetName, 200);
    EXPECT_EQ(ClustersSet({"hahn"}), clusters);
  }

  {
    models::YtTargetInfo target_info;
    target_info.AddYtCluster("hahn", std::nullopt);
    target_info.AddYtCluster("arni", std::nullopt);
    target_info.AddYtCluster("zeno", std::nullopt);
    auto clusters = yt_replica_reader::models::GetAvailableClusters(
        MakeTargets(target_info), kTargetName, 200);
    EXPECT_EQ(ClustersSet({"hahn", "arni", "zeno"}), clusters);
  }

  {
    models::YtTargetInfo target_info;
    target_info.AddYtCluster("hahn", std::nullopt);
    target_info.AddYtCluster("arni", std::nullopt);
    target_info.AddYtCluster("zeno", std::nullopt);
    auto clusters = yt_replica_reader::models::GetAvailableClusters(
        MakeTargets(target_info), kTargetName, std::nullopt);
    EXPECT_EQ(ClustersSet({"hahn", "arni", "zeno"}), clusters);
  }

  {
    models::YtTargetInfo target_info;
    target_info.AddYtCluster("hahn", std::nullopt);
    target_info.AddYtCluster("arni", Timepoint(100));
    target_info.AddYtCluster("zeno", std::nullopt);
    auto clusters = yt_replica_reader::models::GetAvailableClusters(
        MakeTargets(target_info), kTargetName, std::nullopt);
    EXPECT_EQ(ClustersSet({"arni"}), clusters);
  }
}
}  // namespace yt_replica_reader
