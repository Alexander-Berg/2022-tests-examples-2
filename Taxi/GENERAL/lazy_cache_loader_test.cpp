#include <grocery-shared/utils/lazy_cache_loader.hpp>

#include <atomic>

#include <userver/engine/mutex.hpp>
#include <userver/utest/utest.hpp>

#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

namespace {

struct TestLoaderError : public std::runtime_error {
  TestLoaderError() : std::runtime_error::runtime_error{"test error"} {}
};

template <typename T>
void CompileTimeTypeCheck() {
  auto loader = ::grocery_shared::utils::MakeLazyDataLoader(
      []() -> T { throw TestLoaderError{}; });
  static_assert(std::is_same<typename decltype(loader)::Data, T>::value,
                "type mismatch");
}

}  // namespace

TEST(LazyCacheLoader, TypeCheck) {
  CompileTimeTypeCheck<int>();
  CompileTimeTypeCheck<std::string*>();
  CompileTimeTypeCheck<std::reference_wrapper<::engine::Mutex>>();
}

UTEST(LazyCacheLoader, GetOnlyOnce) {
  constexpr int kInitialVal = 42;
  std::atomic_int value{kInitialVal};
  std::atomic_int times_called{0};

  auto loader =
      grocery_shared::utils::MakeLazyDataLoader([&times_called, &value] {
        ++times_called;
        return value.load();
      });
  EXPECT_EQ(times_called, 0);

  EXPECT_EQ(loader.Get(), kInitialVal);
  EXPECT_EQ(times_called, 1);

  value.store(kInitialVal + 1);
  EXPECT_EQ(loader.Get(), kInitialVal);
  EXPECT_EQ(times_called, 1);
}

UTEST(LazyCacheLoader, EmptyAfterMove) {
  const std::optional<std::string> value = "hello world";
  std::atomic_int times_called{0};

  auto loader = grocery_shared::utils::MakeLazyDataLoader(
      [&times_called, &value]() -> std::optional<std::string> {
        ++times_called;
        return value;
      });
  EXPECT_EQ(times_called, 0);

  EXPECT_EQ(loader.Get(), value);
  EXPECT_EQ(times_called, 1);

  EXPECT_EQ(loader.Get(), value);
  EXPECT_EQ(times_called, 1);
}

UTEST(LazyCacheLoader, CheckThrow) {
  std::atomic_int times_called{0};

  auto loader =
      grocery_shared::utils::MakeLazyDataLoader([&times_called]() -> int {
        ++times_called;
        throw TestLoaderError{};
      });

  EXPECT_EQ(times_called, 0);
  for (int i = 0; i != 2; ++i) {
    EXPECT_THROW(loader.Get(), TestLoaderError);
    EXPECT_EQ(times_called, 1);
  }
}

UTEST(LazyCacheLoader, Concurrent) {
  constexpr int kValue = 42;
  constexpr int kIterations = 100;

  std::atomic_int times_called{0};
  auto loader = grocery_shared::utils::MakeLazyDataLoader([&times_called] {
    ++times_called;
    engine::SleepFor(std::chrono::microseconds{500});
    return kValue;
  });

  const auto start_task = [&loader] {
    return ::utils::CriticalAsync("async_lazy_get", [&loader] {
      int ret = 0;
      for (size_t i = 0; i != kIterations; ++i) ret += loader.Get();
      return ret;
    });
  };

  std::vector<decltype(start_task())> tasks(4);
  for (auto& task : tasks) {
    task = start_task();
  }
  for (auto& task : tasks) {
    EXPECT_EQ(task.Get(), kValue * kIterations);
  }
  EXPECT_EQ(times_called, 1);
}
