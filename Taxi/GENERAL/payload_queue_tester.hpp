#include <tasks-control/payload_queue.hpp>

#pragma once

#ifdef ARCADIA_ROOT  // only for C++20

namespace tasks_control::test {

/// Tester class for listener/channel. It can create listener/channel
/// without redis pubsub and emulate passing messages as if received from
/// redis
class PayloadQueueTester {
 public:
  /// Creates test queue
  template <typename Executor, typename... Args>
  inline static auto CreateTestQueue(const Executor& executor) {
    using QueueType = PayloadQueue<Executor, Args...>;
    return std::shared_ptr<QueueType>(
        new QueueType(executor, QueueType::kNoAutoDispatch));
  }

  /// Init dispatcher for given queue
  inline void QueueStartDispatch(auto& queue) {
    LOG_DEBUG() << "Starting queue dispatch";
    queue.StartDispatcherTask();
  }

  /// Stop queue dispatch. This action can not be undone. This method is
  /// used in tests to controllably terminate queue without destroying queue
  /// object itself - for example, to check statistics and some other
  /// post-mortem invariants
  inline void QueueEndDispatch(auto& queue) {
    LOG_DEBUG() << "Stopping queue dispatch";
    queue.EndDispatch();
  }

  /// Waits while queue has no more messages. Returns true if success,
  /// false if timeout or coroutine is cancelled
  inline bool QueueWaitForEmpty(auto& queue) {
    LOG_DEBUG() << "Waiting for empty queue";
    return queue.WaitForEmptyQueue();
  }

  /// Waits while queue has no more messages and all tracked messages
  /// were processed. Returns true if success,
  /// false if timeout or coroutine is cancelled
  inline bool QueueWaitForAll(auto& queue) { return queue.WaitForAll(); }

  template <typename... Args>
  static void SendTestPayload(auto& queue, Args&&... args) {
    queue.OnPayloadReceived(std::forward<Args>(args)...);
  }
};

}  // namespace tasks_control::test

#endif
