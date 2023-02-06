#include <userver/engine/condition_variable.hpp>
#include <userver/engine/mutex.hpp>
#include <userver/utest/utest.hpp>

#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>
#include <userver/utils/mock_now.hpp>

#include "common/function_state_wrapper.hpp"

namespace key_lock_scheduler {

namespace {

using State = FunctionStateWrapper::State;

}

TEST(FunctionStateWrapper, Constructor) {
  bool executed = false;
  {
    FunctionStateWrapper wrapper = [&executed]() { executed = true; };

    EXPECT_EQ(State::kIdle, wrapper.GetState());
    EXPECT_FALSE(wrapper.IsFinished());
    EXPECT_EQ(std::string{}, wrapper.GetError());
  }
  EXPECT_FALSE(executed);
}

TEST(FunctionStateWrapper, Execution) {
  utils::datetime::MockNowUnset();

  RunInCoro(
      [] {
        engine::Mutex mutex;
        engine::ConditionVariable cv;
        bool continue_exec = false;

        FunctionStateWrapper wrapper = [&mutex, &cv, &continue_exec]() {
          std::unique_lock<engine::Mutex> lock(mutex);
          bool ok = cv.Wait(lock, [&continue_exec]() { return continue_exec; });
          EXPECT_TRUE(ok);
        };

        auto wait_for_state_changed = [&wrapper](State initial,
                                                 State expected) {
          auto state_opt = wrapper.WaitForStateChanged(initial);
          EXPECT_TRUE(!!state_opt);
          EXPECT_EQ(expected, *state_opt);
          EXPECT_EQ(expected, wrapper.GetState());
        };

        bool checker1_ready = false;
        int checker1_steps = 2;
        auto checker1 = utils::Async(
            "checker1", [wait_for_state_changed, &mutex, &cv, &checker1_steps,
                         &checker1_ready, &continue_exec]() {
              {
                std::unique_lock<engine::Mutex> lock(mutex);
                checker1_ready = true;
                cv.NotifyAll();
              }

              wait_for_state_changed(State::kIdle, State::kInProgress);
              --checker1_steps;

              {
                std::unique_lock<engine::Mutex> lock(mutex);
                continue_exec = true;
                cv.NotifyAll();
              }

              wait_for_state_changed(State::kInProgress, State::kCompleted);
              --checker1_steps;
            });

        int checker2_steps = 1;
        auto checker2 = utils::Async(
            "checker2", [wait_for_state_changed, &checker2_steps]() {
              wait_for_state_changed(State::kInProgress, State::kCompleted);
              --checker2_steps;
            });

        {
          std::unique_lock<engine::Mutex> lock(mutex);
          EXPECT_TRUE(
              cv.Wait(lock, [&checker1_ready]() { return checker1_ready; }));
        }

        auto worker_task = utils::Async("worker", [&wrapper]() { wrapper(); });
        EXPECT_TRUE(wrapper.WaitForFinished());
        worker_task.Get();

        checker1.Get();
        checker2.Get();
        EXPECT_EQ(0, checker1_steps);
        EXPECT_EQ(0, checker2_steps);

        EXPECT_TRUE(wrapper.IsFinished());
        EXPECT_EQ(std::string{}, wrapper.GetError());
        EXPECT_EQ(State::kCompleted, wrapper.GetState());
      },
      4);
}

TEST(FunctionStateWrapper, Abort) {
  utils::datetime::MockNowUnset();

  RunInCoro(
      [] {
        engine::Mutex mutex;
        engine::ConditionVariable cv;
        bool continue_exec = false;
        const std::string error_str = "fcuk";

        FunctionStateWrapper wrapper = [&mutex, &cv, &continue_exec,
                                        error_str]() {
          std::unique_lock<engine::Mutex> lock(mutex);
          bool ok = cv.Wait(lock, [&continue_exec]() { return continue_exec; });
          EXPECT_TRUE(ok);
          throw std::runtime_error(error_str);
        };

        auto wait_for_state_changed = [&wrapper](State initial,
                                                 State expected) {
          auto state_opt = wrapper.WaitForStateChanged(initial);
          EXPECT_TRUE(!!state_opt);
          EXPECT_EQ(expected, *state_opt);
          EXPECT_EQ(expected, wrapper.GetState());
        };

        bool checker1_ready = false;
        int checker1_steps = 2;
        auto checker1 = utils::Async(
            "checker1", [wait_for_state_changed, &mutex, &cv, &checker1_steps,
                         &checker1_ready, &continue_exec]() {
              {
                std::unique_lock<engine::Mutex> lock(mutex);
                checker1_ready = true;
                cv.NotifyAll();
              }

              wait_for_state_changed(State::kIdle, State::kInProgress);
              --checker1_steps;

              {
                std::unique_lock<engine::Mutex> lock(mutex);
                continue_exec = true;
                cv.NotifyAll();
              }

              wait_for_state_changed(State::kInProgress, State::kAborted);
              --checker1_steps;
            });

        int checker2_steps = 1;
        auto checker2 = utils::Async(
            "checker2", [wait_for_state_changed, &checker2_steps]() {
              wait_for_state_changed(State::kInProgress, State::kAborted);
              --checker2_steps;
            });

        {
          std::unique_lock<engine::Mutex> lock(mutex);
          EXPECT_TRUE(
              cv.Wait(lock, [&checker1_ready]() { return checker1_ready; }));
        }

        auto worker_task = utils::Async(
            "worker", [&wrapper]() { EXPECT_NO_THROW(wrapper()); });
        EXPECT_TRUE(wrapper.WaitForFinished());
        worker_task.Get();

        checker1.Get();
        checker2.Get();
        EXPECT_EQ(0, checker1_steps);
        EXPECT_EQ(0, checker2_steps);

        EXPECT_TRUE(wrapper.IsFinished());
        EXPECT_EQ(error_str, wrapper.GetError());
        EXPECT_EQ(State::kAborted, wrapper.GetState());
      },
      4);
}

}  // namespace key_lock_scheduler
