#include <async_then_sequence.hpp>

#include <vector>

#include <userver/engine/sleep.hpp>
#include <userver/engine/task/cancel.hpp>
#include <userver/utest/utest.hpp>

UTEST(AsyncThenSequence, ConstructDestroy) {
  EXPECT_NO_THROW(pilorama::AsyncThenSequence{});
}

UTEST(AsyncThenSequence, Basic) {
  std::vector<int> data;
  pilorama::AsyncThenSequence a_then;

  a_then.AsyncThen([]() { engine::SleepFor(std::chrono::milliseconds(30)); },
                   [&data]() { data.push_back(1); });

  a_then.AsyncThen([]() { engine::Yield(); }, [&data]() { data.push_back(2); });

  a_then.AsyncThen([]() {}, [&data]() { data.push_back(3); });
  auto task = a_then.Reset();
  task.WaitFor(utest::kMaxTestWaitTime);

  EXPECT_TRUE(task.IsFinished());

  std::vector<int> ethalon{1, 2, 3};
  EXPECT_EQ(data, ethalon);
}

UTEST(AsyncThenSequence, Cancel) {
  std::vector<int> data;
  pilorama::AsyncThenSequence a_then;

  a_then.AsyncThen(
      []() {
        engine::InterruptibleSleepFor(std::chrono::seconds(30));
        engine::current_task::CancellationPoint();
      },
      [&data]() { data.push_back(1); });

  a_then.AsyncThen([]() {}, [&data]() { data.push_back(2); });
  a_then.AsyncThen([]() {}, [&data]() { data.push_back(3); });

  auto task = a_then.Reset();
  task = {};  // cancelling task without throwing exception

  EXPECT_EQ(data, std::vector<int>{});
}

UTEST_MT(AsyncThenSequence, TortureMT, 4) {
  constexpr unsigned count = 1000;
  std::vector<int> data;
  data.reserve(count);
  std::vector<int> ethalon;
  ethalon.reserve(count);

  pilorama::AsyncThenSequence a_then;
  for (unsigned i = 0; i < count; ++i) {
    ethalon.push_back(i);
    a_then.AsyncThen([]() { engine::SleepFor(std::chrono::microseconds(1)); },
                     [&data, i]() { data.push_back(i); });
  }
  auto task = a_then.Reset();
  task.WaitFor(utest::kMaxTestWaitTime);
  EXPECT_TRUE(task.IsFinished());
  EXPECT_EQ(data, ethalon);
}
