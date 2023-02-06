#include "bulk_aggregator.hpp"

#include <userver/engine/task/task_with_result.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

namespace eventus::sinks {

void TestWithAllItemsBeforeDeadline(size_t bulk_size, size_t item_count) {
  using eventus::pipeline::PipelineItem;
  using eventus::pipeline::SeqNum;

  BulkAggregatorSettings settings{static_cast<int>(bulk_size),
                                  std::chrono::seconds(10000), 10000, 10000};

  BulkAggregator aggr = BulkAggregator(settings, "test");

  std::vector<engine::TaskWithResult<void>> tasks;
  for (size_t i = 0; i < item_count; i++) {
    tasks.push_back(::utils::Async("task-" + std::to_string(i), [i, &aggr]() {
      PipelineItem item;
      item.seq_num = i;
      aggr.PushItem(item);
    }));
  }

  for (auto& t : tasks) {
    t.Wait();
  }

  std::unordered_map<SeqNum, int> nums;
  BulkAggregator::BulkItem bulk;

  size_t count = 0;
  while (aggr.GetBulkNoblock(bulk)) {
    ASSERT_EQ(bulk->size(), bulk_size);

    for (size_t i = 0; i < bulk_size; i++) {
      nums[(*bulk)[i].seq_num]++;
    }
    count++;
  }

  ASSERT_EQ(count, item_count / bulk_size);

  for (size_t i = 0; i < item_count; i++) {
    ASSERT_TRUE(nums.find(i) != nums.end());
    ASSERT_EQ(nums[i], 1);
  }
}

UTEST(BulkAggregator, TestAggregationAllItemsBeforeFirstDeadline) {
  TestWithAllItemsBeforeDeadline(2, 1000);
  TestWithAllItemsBeforeDeadline(1, 1000);
  TestWithAllItemsBeforeDeadline(100, 5000);
}

UTEST(BulkAggregator, TestSmallDeadline) {
  using eventus::pipeline::PipelineItem;
  using eventus::pipeline::SeqNum;

  BulkAggregatorSettings settings{10, std::chrono::milliseconds(10), 10000,
                                  10000};

  BulkAggregator aggr = BulkAggregator(settings, "test");

  std::vector<engine::TaskWithResult<void>> tasks;
  for (size_t i = 0; i < 5000; i++) {
    tasks.push_back(::utils::Async("task-" + std::to_string(i), [i, &aggr]() {
      PipelineItem item;
      item.seq_num = i;
      aggr.PushItem(item);
    }));
  }

  for (auto& t : tasks) {
    t.Wait();
  }

  std::unordered_map<SeqNum, int> nums;
  BulkAggregator::BulkItem bulk;

  size_t count = 0;
  while (aggr.GetBulkNoblock(bulk)) {
    ASSERT_TRUE(bulk->size() >= 1 && bulk->size() <= 10);

    for (size_t i = 0; i < bulk->size(); i++) {
      nums[(*bulk)[i].seq_num]++;
    }
    count++;
  }

  ASSERT_TRUE(count >= 500 && count <= 5000);

  for (size_t i = 0; i < 5000; i++) {
    ASSERT_TRUE(nums.find(i) != nums.end());
    ASSERT_EQ(nums[i], 1);
  }
}

}  // namespace eventus::sinks
