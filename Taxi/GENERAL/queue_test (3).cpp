#include <geobus/channels/positions/listener.hpp>
#include <geobus/channels/positions/positions_generator.hpp>
#include <geobus/clients/listener_queue.hpp>
#include "channels/positions/listener_test.hpp"

#include <userver/engine/mutex.hpp>
#include <userver/utils/mock_now.hpp>

#include <userver/engine/condition_variable.hpp>
#include <userver/engine/single_consumer_event.hpp>
#include <userver/engine/sleep.hpp>

namespace geobus::clients {

class GeobusQueueTest : public testing::Test,
                        public generators::PositionsGenerator {};

UTEST_F_MT(GeobusQueueTest, Payload, 2) {
  ::utils::datetime::MockNowSet(std::chrono::system_clock::from_time_t(15000));
  PositionsListener::Payload received_payload;
  bool has_received = false;
  engine::SingleConsumerEvent resume_notification;

  PositionsListenerTester tester;
  GeobusListenerQueue<PositionsListener> geobus_queue(
      [&received_payload, &has_received, &resume_notification](
          const std::string&, PositionsListener::Payload&& payload) {
        received_payload = std::move(payload);
        has_received = true;
        resume_notification.Send();
      },
      20 /*size */);

  EXPECT_EQ(0, geobus_queue.ApproxUnfinishedElementsCount());

  auto listener = tester.CreateTestListener(
      [&geobus_queue](const std::string& channel,
                      PositionsListener::Payload&& payload) {
        geobus_queue.OnPayloadReceived(channel, std::move(payload));
      });

  std::vector<types::DriverPosition> payload;
  payload.push_back(CreateDriverPosition(2));
  payload.push_back(CreateDriverPosition(3));

  tester.SendTestPayload(*listener, payload);
  EXPECT_TRUE(resume_notification.WaitForEvent());

  EXPECT_TRUE(has_received);
  EXPECT_EQ(payload.size(), received_payload.data.size());
  ::utils::datetime::MockNowUnset();
}

UTEST_F_MT(GeobusQueueTest, OverloadByPositions, 2) {
  ::utils::datetime::MockNowSet(std::chrono::system_clock::from_time_t(15000));
  std::vector<size_t> processed_counts;

  // listenr callback will wait at pause_control
  engine::SingleConsumerEvent pause_control;
  // and will send signal via resume_notification when it is finished
  engine::SingleConsumerEvent resume_notification;

  PositionsListenerTester tester;
  auto geobus_queue = tester.CreateTestQueue(
      // This is our callback. It waits at pause_control, then
      // writes payload size to processed counts, and then notifies
      // main coroutine via resume_notification
      [&processed_counts, &pause_control, &resume_notification](
          const std::string&, PositionsListener::Payload&& payload) {
        EXPECT_TRUE(
            pause_control.WaitForEventFor(std::chrono::milliseconds{100}));
        processed_counts.push_back(payload.size());
        resume_notification.Send();
      });

  // Set up queue.
  geobus_queue->SetMaxElementsCount(10);
  geobus_queue->SetEnableTracking(false);

  auto listener = tester.CreateTestListener(
      [&geobus_queue](const std::string& channel,
                      PositionsListener::Payload&& payload) {
        geobus_queue->OnPayloadReceived(channel, std::move(payload));
      });

  // At this moment queue doesn't dispatch elements, and we can safely
  // fill it with messages

  // Queue size is 10. Lets push 3 messages with sizes 2, 10 and 7.

  std::vector<types::DriverPosition> payload2;
  payload2.push_back(CreateDriverPosition(2));
  payload2.push_back(CreateDriverPosition(3));

  std::vector<types::DriverPosition> payload10;
  for (size_t i = 0; i < 10; ++i) {
    payload10.push_back(CreateDriverPosition(i));
  }
  ASSERT_EQ(10, payload10.size());
  std::vector<types::DriverPosition> payload7;
  for (size_t i = 0; i < 7; ++i) {
    payload7.push_back(CreateDriverPosition(i));
  }
  ASSERT_EQ(7, payload7.size());

  tester.SendTestPayload(*listener, payload2);
  tester.SendTestPayload(*listener, payload10);
  tester.SendTestPayload(*listener, payload7);

  // At this moment, queue should contain 3 messages and 19 positions
  // in total
  EXPECT_EQ(19, geobus_queue->ApproxUnfinishedElementsCount());

  // After this, queue dispatcher coroutine will start, calls callback
  // with first payload and pause and wait at pause_control
  // for my signal to continue.
  tester.QueueStartDispatch(*geobus_queue);

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
      1,
      geobus_queue->GetStatistics().skipped_because_overload.messages.Load());
  ::utils::datetime::MockNowUnset();
}

UTEST_F_MT(GeobusQueueTest, TrackingOverloadByTimeout, 2) {
  // Tests checks that if tasks takes longer then allowed time to finish,
  // it is properly cancelled
  engine::SingleConsumerEvent pause_control;
  engine::SingleConsumerEvent resume_notification;

  PositionsListenerTester tester;
  GeobusListenerQueue<PositionsListener> geobus_queue(
      [&pause_control, &resume_notification](const std::string&,
                                             PositionsListener::Payload&&) {
        // pause_control will never fire, instead we should be
        // waked up by cancellation
        EXPECT_FALSE(pause_control.WaitForEvent());
        resume_notification.Send();
      },
      1000 /*queue size*/);
  geobus_queue.SetEnableTracking(true);

  auto listener = tester.CreateTestListener(
      [&geobus_queue](const std::string& channel,
                      PositionsListener::Payload&& payload) {
        geobus_queue.OnPayloadReceived(channel, std::move(payload));
      });

  std::vector<types::DriverPosition> payload;
  payload.push_back(CreateDriverPosition(2));
  payload.push_back(CreateDriverPosition(3));

  tester.SendTestPayload(*listener, payload);

  // Coroutine should be cancelled
  std::ignore = resume_notification.WaitForEvent();

  // TODO: Check number of positions in queue
}

UTEST_F_MT(GeobusQueueTest, TrackingOverloadByTasksCount, 2) {
  // Tests checks that if we try to put more tasks than it is allowed,
  // then old tasks are cancelled

  engine::Mutex pause_control_mutex;
  int pause_control{0};
  engine::ConditionVariable pause_control_cv;

  PositionsListenerTester tester;
  auto geobus_queue = tester.CreateTestQueue(
      [&pause_control_mutex, &pause_control_cv, &pause_control](
          const std::string&, PositionsListener::Payload&&) {
        // pause_control will never fire, instead we should be
        // waked up by cancellation
        std::unique_lock pause_lock{pause_control_mutex};
        EXPECT_FALSE(pause_control_cv.Wait(
            pause_lock, [&pause_control]() { return pause_control == 1; }));
      });
  geobus_queue->SetEnableTracking(true);
  geobus_queue->SetMaxElementsCount(1000);
  geobus_queue->GetTasksControl().SetMaxTasksCount(1);

  auto listener = tester.CreateTestListener(
      [&geobus_queue](const std::string& channel,
                      PositionsListener::Payload&& payload) {
        geobus_queue->OnPayloadReceived(channel, std::move(payload));
      });

  std::vector<types::DriverPosition> payload1;
  payload1.push_back(CreateDriverPosition(2));

  std::vector<types::DriverPosition> payload2{payload1};
  payload2.push_back(CreateDriverPosition(3));

  std::vector<types::DriverPosition> payload4{payload2};
  payload4.push_back(CreateDriverPosition(4));
  payload4.push_back(CreateDriverPosition(5));

  // 3 messages - 3 tracked tasks.
  tester.SendTestPayload(*listener, payload1);
  tester.SendTestPayload(*listener, payload2);
  tester.SendTestPayload(*listener, payload4);

  /// Because tracking is enabled, dispatch will not block. Instead,
  /// first tracked task will block on pause_control, than it will be
  /// cancelled and second corouting should start - and again, pause,
  /// then comes the third corouting. This, in turn, cancelles the second
  /// coroutine.
  tester.QueueStartDispatch(*geobus_queue);
  EXPECT_TRUE(tester.QueueWaitForEmpty(*geobus_queue));

  EXPECT_EQ(2, geobus_queue->GetStatistics().cancelled_too_many_tasks.messages);
  EXPECT_EQ(3,
            geobus_queue->GetStatistics().cancelled_too_many_tasks.positions);

  listener = nullptr;
  geobus_queue = nullptr;
}

UTEST_F_MT(GeobusQueueTest, DiscardByAge, 2) {
  // Tests checks that if tasks takes longer then allowed time to finish,
  // it is properly cancelled
  std::vector<size_t> processed_counts;

  PositionsListenerTester tester;
  auto geobus_queue = tester.CreateTestQueue(
      [&processed_counts](const std::string&,
                          PositionsListener::Payload&& payload) {
        processed_counts.push_back(payload.size());
      });

  geobus_queue->SetMaxElementsCount(1000);
  geobus_queue->SetEnableTracking(false);
  geobus_queue->SetMaxPayloadAge(std::chrono::seconds{600});

  auto listener = tester.CreateTestListener(
      [&geobus_queue](const std::string& channel,
                      PositionsListener::Payload&& payload) {
        geobus_queue->OnPayloadReceived(channel, std::move(payload));
      });

  PositionsListener::Payload payload3;
  for (size_t i = 0; i < 3; ++i) {
    payload3.data.push_back(CreateDriverPosition(i));
  }
  PositionsListener::Payload payload5;
  for (size_t i = 0; i < 5; ++i) {
    payload5.data.push_back(CreateDriverPosition(i));
  }

  ::utils::datetime::MockNowSet(std::chrono::system_clock::from_time_t(15000));
  // This one should pass
  payload3.timestamp = std::chrono::system_clock::from_time_t(14500);
  // And this one should not
  payload5.timestamp = std::chrono::system_clock::from_time_t(14000);

  tester.SendTestPayload(*listener, payload3);
  tester.SendTestPayload(*listener, payload5);

  EXPECT_EQ(0, geobus_queue->GetStatistics().failed_pushs);
  EXPECT_EQ(8, geobus_queue->ApproxUnfinishedElementsCount());

  // After this, queue dispatcher coroutine will pause and wait
  // for my signal to continue.
  tester.QueueStartDispatch(*geobus_queue);
  tester.QueueWaitForEmpty(*geobus_queue);

  EXPECT_EQ(0, geobus_queue->ApproxUnfinishedElementsCount());

  tester.QueueEndDispatch(*geobus_queue);

  std::vector<size_t> reference_counts{3};
  EXPECT_EQ(reference_counts, processed_counts);
  EXPECT_EQ(1, geobus_queue->GetStatistics().skipped_because_age.messages);

  ::utils::datetime::MockNowUnset();
}

}  // namespace geobus::clients
