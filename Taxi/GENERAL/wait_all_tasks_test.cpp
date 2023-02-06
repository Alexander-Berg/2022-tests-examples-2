#include "wait_all_tasks.hpp"
#include <userver/engine/single_consumer_event.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

namespace trackstory {

TEST(WaitAllTasks, Basic) {
  RunInCoro(
      [] {
        engine::SingleConsumerEvent blocking_event;
        auto test_task = utils::Async("test_task", [&blocking_event]() {
          // We wait 5s to allow test to fail if something goes wrong, instead
          // of hanging indefinitely (Actually, CI will kill whole test after
          // like 5 minutes, but timeout of 5 min is overkill. 5 seconds should
          // be enough)
          EXPECT_TRUE(blocking_event.WaitForEventFor(std::chrono::seconds{5}));
        });

        // Can't make this call in main coroutine, because we need to send
        // signal via blocking_event
        auto wait_task = utils::Async("wait_task", [&test_task]() {
          WaitAllTasks(
              test_task,
              // invalid task
              engine::Task{},
              // let's test inline task creation
              utils::Async("inline_task", []() {
                engine::InterruptibleSleepFor(std::chrono::milliseconds{1});
              }));
        });

        blocking_event.Send();
        wait_task.WaitFor(std::chrono::milliseconds{500});
        EXPECT_TRUE(wait_task.IsFinished());
      },
      2);
}

}  // namespace trackstory
