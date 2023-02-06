#include "wait_first.hpp"
#include "wait_first_partitions.hpp"

#include <atomic>
#include <functional>

#include <userver/engine/sleep.hpp>
#include <userver/engine/task/cancel.hpp>
#include <userver/utest/utest.hpp>

namespace yt_replica_reader::utils {
namespace {

const auto kTimeout = std::chrono::milliseconds{100};

class TestError : public std::exception {
  using std::exception::exception;
};

struct BaseTestArgs {
  int expected_ok_requests;
  int expected_error_requests;
  int expected_cancelled_requests;

  BaseTestArgs(int ok, int error, int cancelled)
      : expected_ok_requests(ok),
        expected_error_requests(error),
        expected_cancelled_requests(cancelled) {}
};

struct WaitFirstArgs : public BaseTestArgs {
  std::vector<int> params;
  int parallel_requests;
  bool expected_result;
  std::function<bool(int)> accept;

  WaitFirstArgs(std::vector<int> params, int parallel, bool result, int ok,
                int error, int cancelled, std::function<bool(int)> accept_func)
      : BaseTestArgs(ok, error, cancelled),
        params(std::move(params)),
        parallel_requests(parallel),
        expected_result(result),
        accept(accept_func) {}
};

struct WaitFirstPartitionsArgs : public BaseTestArgs {
  std::vector<int> params;
  std::vector<int> parts_params;
  int parallel_requests;
  bool expected_result;

  WaitFirstPartitionsArgs(std::vector<int> params,
                          std::vector<int> parts_params, int parallel,
                          bool result, int ok, int error, int cancelled)
      : BaseTestArgs(ok, error, cancelled),
        params(std::move(params)),
        parts_params(std::move(parts_params)),
        parallel_requests(parallel),
        expected_result(result) {}
};

template <typename TestFunc>
void DoTest(const BaseTestArgs& args, TestFunc test_func) {
  std::atomic_int ok_requests = 0;
  std::atomic_int error_requests = 0;
  std::atomic_int cancelled_requests = 0;

  // If param > 1, sleep for value
  // If param < 0, throw TestError
  // If param == 0 or param == 1, do nothing and finish with success

  auto do_req = [&](int param) {
    if (param < 0) {
      ++error_requests;
      throw TestError{};
    }

    int ret = 1;
    bool should_cancel = false;

    if (param > 1) {
      engine::InterruptibleSleepFor(std::chrono::milliseconds{param});
      should_cancel = engine::current_task::ShouldCancel();
    }

    if (should_cancel) {
      ++cancelled_requests;
      ret = -1;
    } else {
      ++ok_requests;
    }
    return ret;
  };

  test_func(do_req);

  EXPECT_EQ(args.expected_ok_requests, ok_requests);
  EXPECT_EQ(args.expected_error_requests, error_requests);
  EXPECT_EQ(args.expected_cancelled_requests, cancelled_requests);
}

}  // namespace

class TestWaitFirst : public testing::TestWithParam<WaitFirstArgs> {};

UTEST_P(TestWaitFirst, Tests) {
  auto args = GetParam();

  DoTest(args, [&](auto do_req) {
    concurrent::BackgroundTaskStorage ts;

    auto wf = WaitFirst<int, int>(ts, do_req, args.params,
                                  args.parallel_requests, args.accept);

    if (args.expected_result && (!args.accept || args.accept(1))) {
      ASSERT_EQ(1, wf.Get(kTimeout));
    } else {
      bool has_error = args.params.empty();
      for (const auto x : args.params) {
        if (x < 0 || x > 1) {
          has_error = true;
          break;
        }
      }
      if (has_error)
        ASSERT_THROW(wf.Get(kTimeout),
                     yt_replica_reader::utils::IterationsFailedError);
      else
        ASSERT_THROW(wf.Get(kTimeout),
                     yt_replica_reader::utils::NotAcceptedResultError);
    }
  });
}

INSTANTIATE_UTEST_SUITE_P(
    WaitFirst, TestWaitFirst,
    ::testing::Values(
        // No Requests 0
        WaitFirstArgs{{}, 0, false, 0, 0, 0, nullptr},
        // Single Request 1
        WaitFirstArgs{{0}, 0, true, 1, 0, 0, nullptr},
        // Multiple Requests 2
        WaitFirstArgs{{0, 0}, 0, true, 2, 0, 0, nullptr},
        // Cancel Request 3
        WaitFirstArgs{{0, 5'000}, 0, true, 1, 0, 1, nullptr},
        // Single Request Not Accepted 4
        WaitFirstArgs{{0}, 0, false, 1, 0, 0, [](int) { return false; }},
        // Multiple Requests Not Accepted 5
        WaitFirstArgs{{0, 0}, 0, false, 2, 0, 0, [](int) { return false; }},
        // Cancel Request Not Accepted 6
        WaitFirstArgs{{0, 5'000}, 0, true, 1, 0, 1, [](int) { return false; }},
        // Single Request Accepted 7
        WaitFirstArgs{{0}, 0, true, 1, 0, 0, [](int) { return true; }},
        // Multiple Requests Accepted 8
        WaitFirstArgs{{0, 0}, 0, true, 2, 0, 0, [](int) { return true; }},
        // Cancel Request Accepted 9
        WaitFirstArgs{{0, 5'000}, 0, true, 1, 0, 1, [](int) { return true; }},
        // Cancel All Requests 10
        WaitFirstArgs{{5'000, 5'000}, 0, false, 0, 0, 2, nullptr},
        // Error Request 11
        WaitFirstArgs{{-1, 0}, 0, true, 1, 1, 0, nullptr},
        // Error All Requests 12
        WaitFirstArgs{{-1, -1}, 0, false, 0, 2, 0, nullptr},
        // Sequent Request 13
        WaitFirstArgs{{0, 0, 0}, 1, true, 1, 0, 0, nullptr},
        // Cancel Sequent Request 14
        WaitFirstArgs{{5'000, 5'000, 5'000}, 1, false, 0, 0, 1, nullptr},
        // Error Sequent Request 15
        WaitFirstArgs{{-1, -1, -1}, 1, false, 0, 3, 0, nullptr},
        // 2/3 Parallel Requests 16
        WaitFirstArgs{{0, 0, 0}, 2, true, 2, 0, 0, nullptr},
        // Cancel 2/3 Parallel Requests 17
        WaitFirstArgs{{5'000, 5'000, 5'000}, 2, false, 0, 0, 2, nullptr},
        // Error 2/3 Parallel Requests 18
        WaitFirstArgs{{-1, -1, -1}, 2, false, 0, 3, 0, nullptr}));

////////////////////////////////////////////////////////////////////////////////

class TestWaitFirstPartitions
    : public testing::TestWithParam<WaitFirstPartitionsArgs> {};

UTEST_P(TestWaitFirstPartitions, Tests) {
  auto args = GetParam();

  DoTest(args, [&](auto do_req) {
    concurrent::BackgroundTaskStorage ts;

    auto do_req_wrapper = [&](int part_param, int param) -> int {
      return do_req(param * part_param);
    };
    auto wrapper = [&] {
      return WaitFirstPartitions<int, int, int>(
          ts, do_req_wrapper, args.parts_params, args.params,
          args.parallel_requests, kTimeout, nullptr);
    };

    if (args.expected_result) {
      auto res = wrapper();
      ASSERT_EQ(args.parts_params.size(), res.size());
    } else {
      ASSERT_THROW(wrapper(), std::runtime_error);
    }

    // Reschedule to clear ts
    engine::Yield();
  });
}

INSTANTIATE_UTEST_SUITE_P(
    WaitFirstPartitions, TestWaitFirstPartitions,
    ::testing::Values(
        // No Partitions Requests
        WaitFirstPartitionsArgs{{0}, {}, 0, true, 0, 0, 0},
        // No Internal Requests
        WaitFirstPartitionsArgs{{}, {1}, 0, false, 0, 0, 0},
        // Single Request
        WaitFirstPartitionsArgs{{0}, {1}, 0, true, 1, 0, 0},
        // Multiple Partitions Request
        WaitFirstPartitionsArgs{{0}, {1, 1, 1}, 0, true, 3, 0, 0},
        // Multiple Internal Request
        WaitFirstPartitionsArgs{{0, 0, 0}, {1}, 0, true, 3, 0, 0},
        // Single Partition Error
        WaitFirstPartitionsArgs{{1, 1}, {1, -1}, 0, false, 2, 2, 0},
        // Single Internal Error
        WaitFirstPartitionsArgs{{-1, 1}, {1, 1}, 0, true, 2, 2, 0},
        // Cancel Request
        WaitFirstPartitionsArgs{{0, 5'000}, {1, 1}, 0, true, 2, 0, 2},
        // Cancel All Requests
        WaitFirstPartitionsArgs{{5'000, 5'000}, {1, 1}, 0, false, 0, 0, 4},
        // Sequent Request
        WaitFirstPartitionsArgs{{0, 0}, {1, 1}, 1, true, 2, 0, 0},
        // Cancel Sequent Request
        WaitFirstPartitionsArgs{{5'000, 5'000}, {1, 1}, 1, false, 0, 0, 2},
        // Error Sequent Request
        WaitFirstPartitionsArgs{{-1, -1}, {1, 1}, 1, false, 0, 4, 0},
        // 2/3 Partial Request
        WaitFirstPartitionsArgs{{0, 0, 0}, {1, 1}, 2, true, 4, 0, 0},
        // Cancel 2/3 Partial Request
        WaitFirstPartitionsArgs{
            {5'000, 5'000, 5'000}, {1, 1}, 2, false, 0, 0, 4},
        // Error 2/3 Partial Request
        WaitFirstPartitionsArgs{{-1, -1, -1}, {1, 1}, 2, false, 0, 6, 0}));

}  // namespace yt_replica_reader::utils
