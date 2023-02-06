#include "proximity_semaphore.hpp"

#include <atomic>
#include <vector>

#include <userver/engine/sleep.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

namespace {

using models::identification::Normalize;
using models::identification::Signature;
using std::chrono::milliseconds;
using TimePoint = std::chrono::system_clock::time_point;

const unsigned kDimension = 256;

Signature GenerateNormalizedSignature() {
  Signature result(kDimension, 0.0f);
  for (unsigned i = 0; i < kDimension; ++i) {
    result[i] = (std::rand() % 100) * 0.1f;
  }
  return Normalize(result);
}

}  // namespace

UTEST(ProximitySemaphore, CloseSignatures) {
  const auto kSignaturesCount = 100u;
  std::atomic_int cnt{0};
  std::atomic_int max_cnt{0};

  identification::helpers::ProximitySemaphore sema(20, kDimension);

  std::vector<Signature> signatures;
  signatures.reserve(kSignaturesCount);
  for (auto i = 0; i < kSignaturesCount; ++i) {
    signatures.push_back(GenerateNormalizedSignature());
  }

  std::vector<engine::TaskWithResult<void>> tasks;

  for (unsigned i = 0; i < kSignaturesCount; ++i) {
    auto task =
        utils::Async("task", [i, &sema, &cnt, &max_cnt, &signatures]() mutable {
          auto token = sema.Enter(signatures[i], 3.0);
          auto val = ++cnt;
          max_cnt = std::max<int>(val, max_cnt);  // admissible race
          engine::SleepFor(std::chrono::microseconds(10));
          --cnt;
        });
    tasks.push_back(std::move(task));
    engine::Yield();
  }

  for (auto&& task : tasks) {
    task.Get();
  }

  EXPECT_EQ(1, max_cnt.load());
}

UTEST(ProximitySemaphore, DistantSignatures) {
  const auto kSignaturesCount = 100u;
  std::atomic_int cnt{0};
  std::atomic_int max_cnt{0};

  identification::helpers::ProximitySemaphore sema(20, kDimension);

  std::vector<Signature> signatures;
  signatures.reserve(kSignaturesCount);
  for (auto i = 0; i < kSignaturesCount; ++i) {
    signatures.push_back(GenerateNormalizedSignature());
  }

  std::vector<engine::TaskWithResult<void>> tasks;

  for (unsigned i = 0; i < kSignaturesCount; ++i) {
    auto task =
        utils::Async("task", [i, &sema, &cnt, &max_cnt, &signatures]() mutable {
          auto token = sema.Enter(signatures[i], 0.0);
          auto val = ++cnt;
          max_cnt = std::max<int>(val, max_cnt);  // admissible race
          engine::SleepFor(std::chrono::microseconds(10));
          --cnt;
        });
    tasks.push_back(std::move(task));
    engine::Yield();
  }

  for (auto&& task : tasks) {
    task.Get();
  }

  EXPECT_EQ(20, max_cnt.load());
}
