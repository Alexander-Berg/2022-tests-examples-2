#include <userver/utest/utest.hpp>

#include <memory>

#include <models/stq_workload.hpp>

namespace stq_runner::models {
namespace {
std::shared_ptr<StqWorkload> GetFilledWorkload() {
  auto workload = std::make_shared<StqWorkload>();
  for (auto i = 1; i <= 3; ++i) {
    workload->AddWorker(i);
  }
  for (auto i = 1; i <= 5; ++i) {
    workload->AddTask();
  }
  return workload;
}
}  // namespace

UTEST(StqWorkload, TestAddWorker) {
  StqWorkload workload;
  ASSERT_EQ(0, workload.WorkersCount());

  workload.AddWorker(1);
  workload.AddWorker(2);
  workload.AddWorker(3);
  ASSERT_EQ(3, workload.WorkersCount());

  workload.AddWorker(3);
  workload.AddWorker(3);
  ASSERT_EQ(3, workload.WorkersCount());
}

UTEST(StqWorkload, TestRemoveWorker) {
  auto workload = GetFilledWorkload();

  workload->RemoveWorker(4);
  ASSERT_EQ(3, workload->WorkersCount());

  workload->RemoveWorker(3);
  ASSERT_EQ(2, workload->WorkersCount());

  workload->RemoveWorker(3);
  ASSERT_EQ(2, workload->WorkersCount());
}

UTEST(StqWorkload, TestLeastLoadedWorker) {
  auto workload = GetFilledWorkload();
  ASSERT_EQ(3, workload->LeastLoadedWorker());
}

UTEST(StqWorkload, TestAddTask) {
  auto workload = GetFilledWorkload();
  ASSERT_EQ(3, workload->LeastLoadedWorker());

  workload->AddTask();
  ASSERT_EQ(1, workload->LeastLoadedWorker());

  workload->AddTask();
  ASSERT_EQ(2, workload->LeastLoadedWorker());

  workload->AddTask();
  ASSERT_EQ(3, workload->LeastLoadedWorker());
}

UTEST(StqWorkload, TestRemoveTask) {
  auto workload = GetFilledWorkload();
  ASSERT_EQ(3, workload->LeastLoadedWorker());

  workload->RemoveTask(1);
  ASSERT_EQ(1, workload->LeastLoadedWorker());

  workload->RemoveTask(2);
  ASSERT_EQ(1, workload->LeastLoadedWorker());

  workload->RemoveTask(2);
  ASSERT_EQ(2, workload->LeastLoadedWorker());
}

}  // namespace stq_runner::models
