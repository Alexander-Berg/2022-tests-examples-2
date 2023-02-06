#include <userver/engine/task/single_threaded_task_processors_pool.hpp>
#include <userver/utest/utest.hpp>

UTEST(SingleThreadedTaskprocessor, ConstructionInUserviceTest) {
  const auto pool = engine::SingleThreadedTaskProcessorsPool::MakeForTests(4);
  EXPECT_EQ(pool.GetSize(), 4);
}
