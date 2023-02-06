#include "camera_statistics_keeper.hpp"

#include <cstdlib>

#include <gtest/gtest.h>
#include <userver/engine/task/task_with_result.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

namespace {

using ::models::detection_event_consumer::CameraStatisticsKeeper;
using ::models::detection_event_consumer::kMaxCamerasCount;

struct Input {
  std::string camera_id;
  unsigned identified;
  unsigned unidentified;
};

const unsigned kMaxCounterValue = 1000;

}  // namespace

UTEST(CameraStatisticsKeeperTest, SingleThread) {
  const auto kMaxInputSize = kMaxCamerasCount + 100;

  std::vector<Input> input;
  input.reserve(kMaxInputSize);

  for (auto i = 0ul; i < kMaxInputSize; ++i) {
    input.push_back({"camera_" + std::to_string(i),
                     std::rand() % kMaxCounterValue,
                     std::rand() % kMaxCounterValue});
  }

  CameraStatisticsKeeper statistics;
  unsigned long overall_identified = 0;
  unsigned long overall_unidentified = 0;

  for (auto&& item : input) {
    for (auto i = 0u; i < item.identified; ++i) {
      statistics.IncIdentifiedCounter(item.camera_id);
      ++overall_identified;
    }
    for (auto i = 0u; i < item.unidentified; ++i) {
      statistics.IncUnidentifiedCounter(item.camera_id);
      ++overall_unidentified;
    }
  }

  const auto json_result = statistics.SerializeToJson().ExtractValue();
  EXPECT_EQ(json_result.GetSize(), 3);
  const auto json_cameras = json_result["cameras"];
  EXPECT_EQ(json_cameras.GetSize(), kMaxCamerasCount);
  EXPECT_EQ(json_result["identified"].As<unsigned long>(), overall_identified);
  EXPECT_EQ(json_result["unidentified"].As<unsigned long>(),
            overall_unidentified);

  for (auto i = 0ul; i < input.size(); ++i) {
    const auto item = input[i];
    if (i >= kMaxCamerasCount) {
      EXPECT_FALSE(json_cameras.HasMember(item.camera_id));
      continue;
    }
    EXPECT_TRUE(json_cameras.HasMember(item.camera_id));
    const auto& camera_stats = json_cameras[item.camera_id];
    EXPECT_EQ(camera_stats["identified"].As<unsigned long>(), item.identified);
    EXPECT_EQ(camera_stats["unidentified"].As<unsigned long>(),
              item.unidentified);
  }
}

UTEST(CameraStatisticsKeeperTest, MultiThread) {
  const auto kMaxInputSize = kMaxCamerasCount + 100;

  std::vector<Input> input;
  input.reserve(kMaxInputSize);

  for (auto i = 0ul; i < kMaxInputSize; ++i) {
    input.push_back({"camera_" + std::to_string(i),
                     std::rand() % kMaxCounterValue,
                     std::rand() % kMaxCounterValue});
  }

  CameraStatisticsKeeper statistics;
  std::atomic_uint64_t overall_identified = 0;
  std::atomic_uint64_t overall_unidentified = 0;

  std::atomic_uint64_t indexer = 0;

  std::vector<engine::TaskWithResult<void>> tasks;
  tasks.reserve(10);
  for (auto i = 0ul; i < tasks.capacity(); ++i) {
    tasks.push_back(utils::Async(
        "task", [&indexer, &statistics, &input, &overall_identified,
                 &overall_unidentified]() mutable {
          engine::Yield();
          for (auto idx = indexer.fetch_add(1); idx < input.size();
               idx = indexer.fetch_add(1)) {
            const auto& item = input[idx];

            for (auto i = 0u; i < item.identified; ++i) {
              statistics.IncIdentifiedCounter(item.camera_id);
              ++overall_identified;
            }
            for (auto i = 0u; i < item.unidentified; ++i) {
              statistics.IncUnidentifiedCounter(item.camera_id);
              ++overall_unidentified;
            }
            engine::Yield();
          }
        }));
  }
  for (auto&& task : tasks) {
    task.Get();
  }

  const auto json_result = statistics.SerializeToJson().ExtractValue();
  EXPECT_EQ(json_result.GetSize(), 3);
  const auto json_cameras = json_result["cameras"];
  EXPECT_EQ(json_cameras.GetSize(), kMaxCamerasCount);
  EXPECT_EQ(json_result["identified"].As<unsigned long>(), overall_identified);
  EXPECT_EQ(json_result["unidentified"].As<unsigned long>(),
            overall_unidentified);

  for (auto i = 0ul; i < input.size(); ++i) {
    const auto item = input[i];
    if (i >= kMaxCamerasCount) {
      EXPECT_FALSE(json_cameras.HasMember(item.camera_id));
      continue;
    }
    EXPECT_TRUE(json_cameras.HasMember(item.camera_id));
    const auto& camera_stats = json_cameras[item.camera_id];
    EXPECT_EQ(camera_stats["identified"].As<unsigned long>(), item.identified);
    EXPECT_EQ(camera_stats["unidentified"].As<unsigned long>(),
              item.unidentified);
  }
}
