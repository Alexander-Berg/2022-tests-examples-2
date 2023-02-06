#include <userver/utest/utest.hpp>

#include <internal/unittest_utils/test_utils.hpp>
#include "workers_control.hpp"

UTEST(workers_control, test_workers_count) {
  static const size_t kShardCount = 1;
  static const size_t kWorkersCount = 16;
  static const size_t kShardId = 0;

  driver_route_watcher::test_utils::Env env;
  driver_route_watcher::internal::WorkersControl control(
      kShardCount, kShardId, kWorkersCount, env.deps);
  ASSERT_EQ(kWorkersCount, control.GetWorkersCount());
}
