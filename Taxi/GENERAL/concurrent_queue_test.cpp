#include <userver/utest/utest.hpp>

#include <numeric>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include <boost/range/adaptor/map.hpp>

#include <reposition-shared/utils/as.hpp>
#include <reposition-shared/utils/queue_processor.hpp>

namespace {

namespace rsu = reposition_shared::utils;

const unsigned kReturnElemsSize = 100;

}  // namespace

class TestConcurrentQueueSingleCoro
    : public testing::Test,
      public testing::WithParamInterface<std::tuple<unsigned, unsigned>> {};

INSTANTIATE_UTEST_SUITE_P(TestSingleCoro, TestConcurrentQueueSingleCoro,
                          testing::Values(std::make_tuple(1, 1),
                                          std::make_tuple(1, 3),
                                          std::make_tuple(1, 10)));

UTEST_P(TestConcurrentQueueSingleCoro, TestSingleCoroMultipleQueues) {
  std::vector<unsigned> result;
  const auto kFillResult = [&](auto&& x) { result.push_back(x); };

  const auto [queue_size, iteration_cnt] = GetParam();

  rsu::ConcurrentQueueProcessor<unsigned> concurrent_queue(queue_size);

  for (unsigned j = 0; j < iteration_cnt; ++j) {
    const auto queue_id = concurrent_queue.AssignQueue(kFillResult);
    for (unsigned i = 0; i < kReturnElemsSize; ++i) {
      concurrent_queue.Add(queue_id, i);
    }
    concurrent_queue.WaitForAll(queue_id);
  }

  ASSERT_EQ(kReturnElemsSize * iteration_cnt, result.size());

  std::vector<unsigned> expected(kReturnElemsSize, 0);
  std::iota(expected.begin(), expected.end(), 0);
  const auto exp_cp = expected;
  for (unsigned i = 0; i < iteration_cnt - 1; ++i) {
    expected.insert(expected.end(), exp_cp.begin(), exp_cp.end());
  }

  ASSERT_EQ(result, expected);
}

class TestConcurrentQueue
    : public testing::Test,
      public testing::WithParamInterface<std::tuple<unsigned, unsigned>> {};

INSTANTIATE_TEST_SUITE_P(TestMultipleCoro, TestConcurrentQueue,
                         testing::Values(std::make_tuple(1, 5),
                                         std::make_tuple(5, 10),
                                         std::make_tuple(10, 31)));

TEST_P(TestConcurrentQueue, TestMultipleCoro) {
  std::vector<unsigned> result;
  const auto kFillResult = [&](auto&& x) { result.push_back(x); };

  const auto [queue_size, coro_cnt] = GetParam();

  rsu::ConcurrentQueueProcessor<unsigned> concurrent_queue(queue_size);
  for (unsigned j = 0; j < coro_cnt; ++j) {
    RunInCoro([&]() {
      const auto queue_id = concurrent_queue.AssignQueue(kFillResult);
      for (unsigned i = 0; i < kReturnElemsSize; ++i) {
        concurrent_queue.Add(queue_id, i);
      }
      concurrent_queue.WaitForAll(queue_id);
    });
  }

  ASSERT_EQ(kReturnElemsSize * coro_cnt, result.size());

  std::unordered_map<unsigned, int> cnt_nums;
  for (const auto num : result) {
    cnt_nums[num]++;
  }
  for (const auto& [_, cnt] : cnt_nums) {
    ASSERT_EQ(cnt, coro_cnt);
  }

  const auto num_set = rsu::As<std::unordered_set<unsigned>>(
      cnt_nums | boost::adaptors::map_keys);

  std::vector<unsigned> expected_vec(kReturnElemsSize, 0);
  std::iota(expected_vec.begin(), expected_vec.end(), 0);
  const auto expected_set = rsu::As<std::unordered_set<unsigned>>(expected_vec);

  ASSERT_EQ(num_set, expected_set);
}
