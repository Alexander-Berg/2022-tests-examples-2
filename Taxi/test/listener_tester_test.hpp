#pragma once

#include <geobus/clients/listener_channel.hpp>
#include <geobus/clients/listener_queue.hpp>

namespace geobus::test {

/// Tester class for listener/channel. It can create listener/channel
/// without redis pubsub and emulate passing messages as if received from
/// redis
template <typename ListenerType>
class GeobusListenerTester {
 public:
  using Listener = ListenerType;
  using Payload = typename Listener::Payload;
  using RawPayload = typename Listener::RawPayload;
  using Channel = ::geobus::clients::GeobusListenerChannel<ListenerType>;
  using Queue = ::geobus::clients::GeobusListenerQueue<ListenerType>;
  /// Creates test listener
  inline static std::shared_ptr<Listener> CreateTestListener(
      typename Listener::CallbackType callback) {
    return std::shared_ptr<Listener>(new Listener(callback));
  }

  inline static std::shared_ptr<Listener> CreateTestListener(
      std::shared_ptr<Channel> channel) {
    // Can't use make_shared because constructor is private
    return std::shared_ptr<Listener>(
        new Listener([channel(std::move(channel))](const auto& redis_channel,
                                                   auto&& payload) {
          channel->OnPayloadReceived(redis_channel, std::move(payload));
        }));
  }

  /// Creates test channel
  inline static std::shared_ptr<Channel> CreateTestChannel() {
    using DebugTag = typename Channel::DebugTag;
    DebugTag debug_tag;
    return std::shared_ptr<Channel>(new Channel(debug_tag));
  }

  /// Creates test queue
  inline static std::shared_ptr<Queue> CreateTestQueue(
      typename Listener::CallbackType callback) {
    return std::shared_ptr<Queue>(
        new Queue(std::move(callback), Queue::kNoAutoDispatch));
  }

  /// Init dispatcher for given queue
  inline void QueueStartDispatch(Queue& queue) { queue.StartDispatcherTask(); }

  /// Stop queue dispatch. This action can not be undone. This method is
  /// used in tests to controllably terminate queue without destroying queue
  /// object itself - for example, to check statistics and some other
  /// post-mortem invariants
  inline void QueueEndDispatch(Queue& queue) { queue.EndDispatch(); }

  /// Waits while queue has no more messages. Returns true if success,
  /// false if timeout or coroutine is cancelled
  inline bool QueueWaitForEmpty(Queue& queue) {
    return queue.WaitForEmptyQueue();
  }

  /// Waits while queue has no more messages and all tracked messages
  /// were processed. Returns true if success,
  /// false if timeout or coroutine is cancelled
  inline bool QueueWaitForAll(Queue& queue) { return queue.WaitForAll(); }

  /// Send test message emulating redis channel
  static void SendTestMessage(Listener& target, const std::string& payload);
  /// Send test payload skipping redis deserialization - as if given
  /// \p payload is actually what has been received from redis
  static void SendTestPayload(Listener& target, const RawPayload& payload);
  static void SendTestPayload(Listener& target, RawPayload&& payload);
  static void SendTestPayload(Listener& target, const Payload& payload);
  static void SendTestPayload(Listener& target, Payload&& payload);
};

template <typename ListenerType>
void GeobusListenerTester<ListenerType>::SendTestMessage(
    Listener& target, const std::string& payload) {
  target.TestSendMessage("test_channel", payload);
}

template <typename ListenerType>
void GeobusListenerTester<ListenerType>::SendTestPayload(
    Listener& target, const RawPayload& payload) {
  target.TestSendPayload("test_channel", RawPayload{payload});
}

template <typename ListenerType>
void GeobusListenerTester<ListenerType>::SendTestPayload(Listener& target,
                                                         RawPayload&& payload) {
  target.TestSendPayload("test_channel", std::move(payload));
}

template <typename ListenerType>
void GeobusListenerTester<ListenerType>::SendTestPayload(
    Listener& target, const Payload& payload) {
  target.TestSendPayload("test_channel", Payload{payload});
}

template <typename ListenerType>
void GeobusListenerTester<ListenerType>::SendTestPayload(Listener& target,
                                                         Payload&& payload) {
  target.TestSendPayload("test_channel", std::move(payload));
}

}  // namespace geobus::test
