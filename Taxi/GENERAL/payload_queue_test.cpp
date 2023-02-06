#ifdef ARCADIA_ROOT  // only for C++20

#include <tasks-control/payload_queue.hpp>
#include <tasks-control/payload_queue_tester.hpp>

#include <userver/engine/mutex.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <userver/engine/condition_variable.hpp>
#include <userver/engine/single_consumer_event.hpp>
#include <userver/engine/sleep.hpp>

namespace tasks_control::test {

class PayloadQueueTest : public testing::Test

{
 public:
  struct Element {
    size_t a{42};
    double b{36.0};
  };

  struct Payload : public std::vector<Element> {
    std::chrono::system_clock::time_point timestamp;

    Payload() = default;
    Payload(Payload&&) = default;
    Payload& operator=(Payload&&) = default;
    // block copy and assign. we make them explicit because in tests
    // we do need to copy them
    explicit Payload(const Payload&) = default;
    Payload& operator=(const Payload&) = delete;
  };

  Element CreateElement(size_t seed) {
    return Element{seed / 2 * 3, seed * 1.0 / 42.0};
  }

  Payload CreatePayload(size_t seed, size_t count = 5) {
    Payload result;
    for (size_t i = 0; i < count; ++i) {
      result.emplace_back(CreateElement(seed + i));
    }
    result.timestamp = ::utils::datetime::Now();
    return result;
  }

  static constexpr bool kStartQueue = true;
  static constexpr bool kNoStartQueue = false;

  template <typename Callback>
  auto CreateQueue(Callback callback, bool auto_start = false) {
    FnExecutor executor{
        // execute fn
        [callback](const std::string& s, Payload&& payload) {
          LOG_DEBUG() << "Calling user callback for " << s;
          callback(s, std::move(payload));
        },
        // size fn
        [](const std::string&, const Payload& payload) {
          return payload.size();
        },
        // timestamp_fn
        [](const std::string&, const Payload& p) { return p.timestamp; }};

    auto res = tester.CreateTestQueue<decltype(executor), std::string, Payload>(
        executor);
    if (auto_start) {
      tester.QueueStartDispatch(*res);
    }

    return res;
  }

  PayloadQueueTester tester;
};

UTEST_F(PayloadQueueTest, DeductionGuides) {
  size_t sz = 7;
  // test deduction guides for FnExecutor
  FnExecutor executor{
      [](const std::string&, Payload&&) {},
      [](const std::string&, const Payload& p) { return p.size(); },
      [](const std::string&, const Payload&) {
        return std::chrono::system_clock::now();
      }};

  executor.Execute("test", CreatePayload(43, sz));
  EXPECT_EQ(executor.GetSize("test", CreatePayload(42, sz)), sz);

  // test deduction guides for PayloadQueue
  const size_t queue_size = 20;
  PayloadQueue<decltype(executor), std::string, Payload> bus_queue{executor,
                                                                   queue_size};
  bus_queue.OnPayloadReceived(std::string{"test"}, CreatePayload(43, sz));
}

UTEST_F_MT(PayloadQueueTest, Payload, 2) {
  ::utils::datetime::MockNowSet(std::chrono::system_clock::from_time_t(15000));
  Payload received_payload;
  bool has_received = false;
  engine::SingleConsumerEvent resume_notification;

  auto bus_queue = CreateQueue(
      [&received_payload, &has_received, &resume_notification](
          const std::string&, Payload&& payload) {
        received_payload = std::move(payload);
        has_received = true;
        resume_notification.Send();
      },
      kStartQueue);

  EXPECT_EQ(0, bus_queue->ApproxUnfinishedElementsCount());

  const Payload reference_payload = CreatePayload(17);

  bus_queue->OnPayloadReceived(std::string("test"), Payload{reference_payload});
  EXPECT_TRUE(resume_notification.WaitForEvent());

  EXPECT_TRUE(has_received);
  EXPECT_EQ(reference_payload.size(), received_payload.size());
  ::utils::datetime::MockNowUnset();

  LOG_DEBUG() << "Test finished";
}

UTEST_F_MT(PayloadQueueTest, OverloadByPositions, 2) {
  ::utils::datetime::MockNowSet(std::chrono::system_clock::from_time_t(15000));
  std::vector<size_t> processed_counts;

  // listenr callback will wait at pause_control
  engine::SingleConsumerEvent pause_control;
  // and will send signal via resume_notification when it is finished
  engine::SingleConsumerEvent resume_notification;

  auto bus_queue = CreateQueue(
      // This is our callback. It waits at pause_control, then
      // writes payload size to processed counts, and then notifies
      // main coroutine via resume_notification
      [&processed_counts, &pause_control, &resume_notification](
          const std::string&, Payload&& payload) {
        EXPECT_TRUE(
            pause_control.WaitForEventFor(std::chrono::milliseconds{100}));
        processed_counts.push_back(payload.size());
        resume_notification.Send();
      },
      kNoStartQueue);

  // Set up queue.
  bus_queue->SetMaxElementsCount(10);
  bus_queue->SetEnableTracking(false);

  // At this moment queue doesn't dispatch elements, and we can safely
  // fill it with messages

  // Queue size is 10. Lets push 3 messages with sizes 2, 10 and 7.

  Payload payload2 = CreatePayload(23, 2);
  ASSERT_EQ(2, payload2.size());

  Payload payload10 = CreatePayload(27, 10);
  ASSERT_EQ(10, payload10.size());

  Payload payload7 = CreatePayload(29, 7);
  ASSERT_EQ(7, payload7.size());

  tester.SendTestPayload(*bus_queue, "test_size_2", Payload{payload2});
  tester.SendTestPayload(*bus_queue, "test_size_10", Payload{payload10});
  tester.SendTestPayload(*bus_queue, "test_size+7", Payload{payload7});

  // At this moment, queue should contain 3 messages and 19 positions
  // in total
  EXPECT_EQ(19, bus_queue->ApproxUnfinishedElementsCount());

  // After this, queue dispatcher coroutine will start, calls callback
  // with first payload and pause and wait at pause_control
  // for my signal to continue.
  tester.QueueStartDispatch(*bus_queue);

  const auto kWaitLimit = std::chrono::milliseconds{10};

  // first message should be ignored, second and third should be parsed
  // send three times to catch possible errors
  pause_control.Send();
  EXPECT_TRUE(resume_notification.WaitForEventFor(kWaitLimit));

  pause_control.Send();
  EXPECT_TRUE(resume_notification.WaitForEventFor(kWaitLimit));

  pause_control.Send();

  // Don't wait third time! If test is working as expected, than only 2
  // messages in total will be parsed and only 2 resume notifications will
  // be send
  // ASSERT_TRUE(resume_notification.WaitForEvent());

  std::vector<size_t> reference_counts{10, 7};
  EXPECT_EQ(reference_counts, processed_counts);

  EXPECT_EQ(
      1, bus_queue->GetStatistics().skipped_because_overload.messages.Load());
  ::utils::datetime::MockNowUnset();
  LOG_DEBUG() << "Test finished";
}

UTEST_F_MT(PayloadQueueTest, TrackingOverloadByTimeout, 2) {
  // Tests checks that if tasks takes longer then allowed time to finish,
  // it is properly cancelled
  engine::SingleConsumerEvent pause_control;
  engine::SingleConsumerEvent resume_notification;

  auto bus_queue = CreateQueue(
      [&pause_control, &resume_notification](const std::string&, Payload&&) {
        // pause_control will never fire, instead we should be
        // waked up by cancellation
        EXPECT_FALSE(pause_control.WaitForEvent());
        resume_notification.Send();
      },
      kStartQueue);
  bus_queue->SetMaxElementsCount(1000);
  bus_queue->SetEnableTracking(true);

  Payload payload = CreatePayload(41, 2);

  tester.SendTestPayload(*bus_queue, "test1", std::move(payload));

  // Coroutine should be cancelled
  std::ignore = resume_notification.WaitForEvent();

  // TODO: Check number of positions in queue
}

UTEST_F_MT(PayloadQueueTest, TrackingOverloadByTasksCount, 2) {
  // Tests checks that if we try to put more tasks than it is allowed,
  // then old tasks are cancelled

  engine::Mutex pause_control_mutex;
  int pause_control{0};
  engine::ConditionVariable pause_control_cv;

  auto bus_queue = CreateQueue([&pause_control_mutex, &pause_control_cv,
                                &pause_control](const std::string&, Payload&&) {
    // pause_control will never fire, instead we should be
    // waked up by cancellation
    std::unique_lock pause_lock{pause_control_mutex};
    EXPECT_FALSE(pause_control_cv.Wait(
        pause_lock, [&pause_control]() { return pause_control == 1; }));
  });
  bus_queue->SetEnableTracking(true);
  bus_queue->SetMaxElementsCount(1000);
  bus_queue->GetTasksControl().SetMaxTasksCount(1);

  Payload payload1 = CreatePayload(42, 1);

  Payload payload2 = CreatePayload(42, 2);

  Payload payload4 = CreatePayload(42, 4);

  // 3 messages - 3 tracked tasks.
  tester.SendTestPayload(*bus_queue, "test1", std::move(payload1));
  tester.SendTestPayload(*bus_queue, "test2", std::move(payload2));
  tester.SendTestPayload(*bus_queue, "test4", std::move(payload4));

  /// Because tracking is enabled, dispatch will not block. Instead,
  /// first tracked task will block on pause_control, than it will be
  /// cancelled and second corouting should start - and again, pause,
  /// then comes the third corouting. This, in turn, cancelles the second
  /// coroutine.
  tester.QueueStartDispatch(*bus_queue);
  EXPECT_TRUE(tester.QueueWaitForEmpty(*bus_queue));

  EXPECT_EQ(2, bus_queue->GetStatistics().cancelled_too_many_tasks.messages);
  EXPECT_EQ(3, bus_queue->GetStatistics().cancelled_too_many_tasks.positions);

  bus_queue = nullptr;
}

UTEST_F_MT(PayloadQueueTest, DiscardByAge, 2) {
  // Tests checks that if tasks takes longer then allowed time to finish,
  // it is properly cancelled
  std::vector<size_t> processed_counts;

  auto bus_queue = CreateQueue(
      [&processed_counts](const std::string&, Payload&& payload) {
        processed_counts.push_back(payload.size());
      },
      kNoStartQueue);

  bus_queue->SetMaxElementsCount(1000);
  bus_queue->SetEnableTracking(false);
  bus_queue->SetMaxPayloadAge(std::chrono::seconds{600});

  Payload payload3 = CreatePayload(42, 3);
  Payload payload5 = CreatePayload(42, 5);

  ::utils::datetime::MockNowSet(std::chrono::system_clock::from_time_t(15000));
  // This one should pass
  payload3.timestamp = std::chrono::system_clock::from_time_t(14500);
  // And this one should not
  payload5.timestamp = std::chrono::system_clock::from_time_t(14000);

  tester.SendTestPayload(*bus_queue, "test3", std::move(payload3));
  tester.SendTestPayload(*bus_queue, "test5", std::move(payload5));

  EXPECT_EQ(0, bus_queue->GetStatistics().failed_pushs);
  EXPECT_EQ(8, bus_queue->ApproxUnfinishedElementsCount());

  // After this, queue dispatcher coroutine will pause and wait
  // for my signal to continue.
  tester.QueueStartDispatch(*bus_queue);
  tester.QueueWaitForEmpty(*bus_queue);

  EXPECT_EQ(0, bus_queue->ApproxUnfinishedElementsCount());

  tester.QueueEndDispatch(*bus_queue);

  std::vector<size_t> reference_counts{3};
  EXPECT_EQ(reference_counts, processed_counts);
  EXPECT_EQ(1, bus_queue->GetStatistics().skipped_because_age.messages);

  ::utils::datetime::MockNowUnset();
}

}  // namespace tasks_control::test

#endif
