#include "context.hpp"

#include <models/exceptions.hpp>
#include <scoring/execution/js/utils/watch_for_js_future.hpp>
#include "task.hpp"
#include "userver/utils/assert.hpp"

#include <userver/utils/assert.hpp>

namespace driver_scoring::admin::script_tests::execution::js {

namespace {

const std::string kTaskWaiterName = "script_tests_task_waiter";

}  // namespace

Context::Context(std::shared_ptr<Environment> env) {
  UINVARIANT(env, "Environment is nullptr");

  deadline_ = engine::Deadline::FromDuration(env->timeout);
  size_t test_count = env->request.tests.size();
  std::vector<PromiseType> promises(test_count);
  futures_.resize(test_count);
  for (size_t test_idx = 0; test_idx < test_count; ++test_idx) {
    futures_[test_idx] = promises[test_idx].get_future();
  }
  execution_info_ = std::make_shared<scoring::execution::js::ExecutionInfo>();
  auto timeout = env->timeout;
  auto future = env->js_component.Execute<bool>(
      std::make_unique<Task>(env, std::move(promises), execution_info_));
  scoring::execution::js::utils::WatchForJsFuture(
      kTaskWaiterName, std::move(future), timeout, execution_info_);
}

Result Context::Context::GetResult(size_t test_idx) {
  if (auto state = execution_info_->WaitWhileNotStarted(deadline_);
      state != models::ExecutionState::kStarted) {
    return Result{Status::kTimeout};
  }
  try {
    return futures_[test_idx].get(deadline_.TimeLeft());
  } catch (utils::FutureTimeoutError& err) {
    execution_info_->SetStateAndNotify(models::ExecutionState::kTimeout,
                                       models::ExecutionState::kStarted);
    return Result{Status::kTimeout};
  } catch (const std::exception& exc) {
    Result res{Status::kRuntimeError};
    res.message = exc.what();
    return res;
  }
}

}  // namespace driver_scoring::admin::script_tests::execution::js
