#include "async.hpp"
#include <utils/weak_bind.hpp>

#include <gtest/gtest.h>

const size_t kCount = 16;
const size_t kPoolSize = 8;

TEST(Async, Call) {
  utils::Async async(kPoolSize, "test", false);

  using Future = utils::Async::Future<size_t>;

  std::vector<Future> futures;
  futures.reserve(kCount);

  for (size_t i = 0; i < kCount; ++i) {
    futures.emplace_back(async.Call([i]() {
      std::this_thread::sleep_for(std::chrono::seconds(1));
      return i;
    }));
  }

  for (size_t i = 0; i < kCount; ++i) {
    EXPECT_EQ(i, futures[i].Get());
  }
  async.Stop();
}

TEST(Async, Call2) {
  utils::Async async(kPoolSize, "test", false);

  using Future = utils::Async::Future<void>;

  std::vector<Future> futures;
  futures.reserve(kCount);

  std::vector<size_t> result(kCount, -1);
  for (size_t i = 0; i < kCount; ++i) {
    size_t& out = result[i];
    futures.emplace_back(async.Call([i, &out]() {
      std::this_thread::sleep_for(std::chrono::seconds(1));
      out = i;
    }));
  }

  for (size_t i = 0; i < kCount; ++i) {
    futures[i].Wait();
  }

  for (size_t i = 0; i < kCount; ++i) {
    EXPECT_EQ(i, result[i]);
  }
  async.Stop();
}

TEST(Async, CallPeriodically) {
  utils::Async async(kPoolSize, "test", false);

  std::atomic<size_t> cnt(0);

  async.CallPeriodically(
      std::chrono::milliseconds(100),
      [&cnt](const utils::Async::Status&, TimeStorage&, LogExtra&) { ++cnt; },
      "test", true);

  sleep(2);

  EXPECT_LE(15lu, cnt);
  EXPECT_GE(25lu, cnt);
  async.Stop();
}

namespace {

class AsyncCaller {
 public:
  AsyncCaller(std::atomic<size_t>& var) : var_(var) {}

  void Foo(const utils::AsyncStatus&, TimeStorage&) { ++var_; }

 private:
  std::atomic<size_t>& var_;
};

}  // namespace

TEST(Async, CallPeriodicallyWeak) {
  utils::Async async(1, "test", false);

  std::atomic<size_t> cnt(0);
  auto caller = std::make_shared<AsyncCaller>(cnt);

  async.CallPeriodically(
      std::chrono::milliseconds(110),
      [&cnt, &caller](const utils::Async::Status&, TimeStorage&, LogExtra&) {
        if (cnt >= 3) caller.reset();
      },
      "deleter");

  async.CallPeriodically(
      std::chrono::milliseconds(100),
      utils::WeakBindThrowable(&AsyncCaller::Foo, caller, std::placeholders::_1,
                               std::placeholders::_2),
      "test", true);

  std::this_thread::sleep_for(std::chrono::seconds(2));

  EXPECT_EQ(3u, cnt);
  async.Stop();
}

TEST(Async, CallPeriodicallyStrong) {
  utils::Async async(kPoolSize, "test", false);

  std::atomic<size_t> cnt(0);

  async.CallPeriodicallyStrong(
      std::chrono::milliseconds(100),
      [&cnt](const utils::Async::Status&, TimeStorage&, LogExtra&) {
        ++cnt;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
      },
      "test", true);

  std::this_thread::sleep_for(std::chrono::seconds(2));

  EXPECT_LE(15lu, cnt);
  EXPECT_GE(25lu, cnt);
  async.Stop();
}

TEST(Async, CallPeriodicallyChaotic) {
  utils::Async async(kPoolSize, "test", false);

  std::atomic<size_t> cnt(0);

  async.CallPeriodicallyChaotic(
      std::chrono::milliseconds(100),
      [&cnt](const utils::Async::Status&, TimeStorage&, LogExtra&) {
        ++cnt;
        std::this_thread::sleep_for(std::chrono::milliseconds(75));
      },
      "test", true);

  std::this_thread::sleep_for(std::chrono::seconds(2));

  EXPECT_LE(15lu, cnt);
  EXPECT_GE(25lu, cnt);
  async.Stop();
}

TEST(Async, CallPeriodicallyChaotic2) {
  utils::Async async(kPoolSize, "test", false);

  std::atomic<size_t> cnt(0);

  async.CallPeriodicallyChaotic(
      std::chrono::milliseconds(1000),  // success
      std::chrono::milliseconds(100),   // failure
      [&cnt](const utils::Async::Status&, TimeStorage&, LogExtra&) {
        ++cnt;
        std::this_thread::sleep_for(std::chrono::milliseconds(75));
        throw std::runtime_error("failed, use second period");
      },
      "test", true);

  std::this_thread::sleep_for(std::chrono::seconds(2));

  EXPECT_LE(15lu, cnt);
  EXPECT_GE(25lu, cnt);
  async.Stop();
}

TEST(Async, Parallel) {
  utils::Async async(kPoolSize, "test", false);

  size_t i0, i1, i2;

  std::tie(i0) = async.Parallel([]() { return 0lu; });

  EXPECT_LE(0lu, i0);

  std::tie(i0, i1, i2) = async.Parallel(
      []() { return 0lu; }, []() { return 1lu; }, []() { return 2lu; });

  EXPECT_LE(0lu, i0);
  EXPECT_LE(1lu, i1);
  EXPECT_LE(2lu, i2);
  async.Stop();
}

TEST(Async, Deadlock) {
  utils::Async async(kPoolSize, "test", false);
  // the follwing code will require utils::kAsyncNumThreads + 1 threads
  std::atomic_uint flag;
  auto future = async.Call([&] {
    std::vector<utils::Async::Future<int>> futures;
    flag = 0u;
    auto checker = [&flag] {
      flag++;
      while (flag < kPoolSize) {
        std::this_thread::yield();
      }
      return 0;
    };
    for (size_t i = 0u; i < kPoolSize; ++i) {
      futures.emplace_back(async.Call(checker));
    }
    for (auto& f : futures) {
      f.Wait();
    }
  });
  ASSERT_EQ(std::future_status::ready, future.WaitFor(std::chrono::seconds(2)));
  ASSERT_EQ(kPoolSize, flag);
  async.Stop();
}

TEST(Async, DISABLED_DontThrowAfter60Seconds) {
  utils::Async async(1, "test", false);
  auto future = async.Call(
      []() { std::this_thread::sleep_for(std::chrono::seconds(70)); });

  ASSERT_NO_THROW(future.Wait());
  async.Stop();
}
