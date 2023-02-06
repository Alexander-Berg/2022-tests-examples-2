#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <userver/engine/mpsc_queue.hpp>
#include <userver/utils/datetime.hpp>

#include <chrono>

#include <utils/deduplicator.hpp>

namespace {
using DeduplicatorKeyType = std::string;
using TestDeduplicator = utils::Deduplicator<DeduplicatorKeyType>;
using namespace std::literals::chrono_literals;

const auto kMockTime = utils::datetime::Now();
const TestDeduplicator::Settings kDefaultSettings{100ms, 0};

}  // namespace

UTEST(DeduplicatorSuite, FirstIncomingTest) {
  ::utils::datetime::MockNowSet(kMockTime);
  TestDeduplicator dedup(kDefaultSettings);

  ASSERT_TRUE(dedup.Register("unique-key", kMockTime));
}

UTEST(DeduplicatorSuite, ReEnqueuedItemTest) {
  ::utils::datetime::MockNowSet(kMockTime);
  TestDeduplicator dedup(kDefaultSettings);

  ASSERT_TRUE(dedup.Register("unique-key", kMockTime));
  ASSERT_TRUE(dedup.Register("unique-key", kMockTime));
  ::utils::datetime::MockNowSet(kMockTime + 10ms);
  ASSERT_TRUE(dedup.Register("unique-key", kMockTime));
}

UTEST(DeduplicatorSuite, PassingTimeoutTest) {
  ::utils::datetime::MockNowSet(kMockTime);
  TestDeduplicator dedup(kDefaultSettings);

  ASSERT_TRUE(dedup.Register("unique-key", kMockTime));
  ::utils::datetime::MockNowSet(kMockTime + 100ms);
  ASSERT_TRUE(dedup.Register("unique-key", kMockTime + 110ms));
}

UTEST(DeduplicatorSuite, DeduplicateTest) {
  ::utils::datetime::MockNowSet(kMockTime);
  TestDeduplicator dedup(kDefaultSettings);

  ASSERT_TRUE(dedup.Register("unique-key", kMockTime));
  ASSERT_FALSE(dedup.Register("unique-key", kMockTime + 10ms));
  ASSERT_FALSE(dedup.Register("unique-key", kMockTime + 20ms));

  ::utils::datetime::MockNowSet(kMockTime + 100ms);
  ASSERT_TRUE(dedup.Register("unique-key", kMockTime + 100ms));
  ASSERT_FALSE(dedup.Register("unique-key", kMockTime + 110ms));
  // check an old item will be dropped also,
  // e.g. if it come with in-queue delay
  ASSERT_FALSE(dedup.Register("unique-key", kMockTime + 10ms));
}

namespace {
template <typename QueueItem, typename Consumer>
std::pair<size_t, size_t> GetItemsInQueueCount(const Consumer& consumer) {
  size_t items_in_queue = 0;
  size_t bad_items = 0;
  QueueItem item;
  while (consumer.PopNoblock(item)) {
    if (item) {
      items_in_queue++;
    } else {
      bad_items++;
    }
  }
  return {items_in_queue, bad_items};
}
}  // namespace

UTEST(DeduplicatorSuite, CompressionQueueTest) {
  ::utils::datetime::MockNowSet(kMockTime);
  TestDeduplicator dedup({0s, 1u, 5s});

  using ItemType = std::string;
  using QueueItem = std::unique_ptr<ItemType>;
  auto queue = engine::MpscQueue<QueueItem>::Create();
  auto consumer = queue->GetConsumer();
  auto producer = queue->GetProducer();

  {
    for (int dups = 0; dups < 10; dups++) {
      for (int unique = 0; unique < 5; unique++) {
        auto item = std::make_unique<ItemType>(fmt::format("value-{}", unique));
        ASSERT_TRUE(producer.Push(
            std::move(item),
            engine::Deadline::FromDuration(std::chrono::milliseconds(50))));
      }
    }

    dedup.CompressQueue<ItemType>(
        consumer, producer, 50,
        [](const ItemType& item) -> DeduplicatorKeyType { return item; });

    const auto& [items_in_queue, bad_items] =
        GetItemsInQueueCount<QueueItem>(consumer);
    ASSERT_EQ(items_in_queue, 5);
    ASSERT_EQ(bad_items, 0);
  }

  // do not compress too frequently
  {
    for (int dups = 0; dups < 2; dups++) {
      for (int unique = 0; unique < 5; unique++) {
        auto item = std::make_unique<ItemType>(fmt::format("value-{}", unique));
        ASSERT_TRUE(producer.Push(
            std::move(item),
            engine::Deadline::FromDuration(std::chrono::milliseconds(50))));
      }
    }

    dedup.CompressQueue<ItemType>(
        consumer, producer, 50,
        [](const ItemType& item) -> DeduplicatorKeyType { return item; });

    const auto& [items_in_queue, bad_items] =
        GetItemsInQueueCount<QueueItem>(consumer);
    ASSERT_EQ(items_in_queue, 10);
    ASSERT_EQ(bad_items, 0);
  }

  {
    for (int dups = 0; dups < 2; dups++) {
      for (int unique = 0; unique < 5; unique++) {
        auto item = std::make_unique<ItemType>(fmt::format("value-{}", unique));
        ASSERT_TRUE(producer.Push(
            std::move(item),
            engine::Deadline::FromDuration(std::chrono::milliseconds(50))));
      }
    }

    ::utils::datetime::MockNowSet(kMockTime + 6s);
    dedup.CompressQueue<ItemType>(
        consumer, producer, 50,
        [](const ItemType& item) -> DeduplicatorKeyType { return item; });

    const auto& [items_in_queue, bad_items] =
        GetItemsInQueueCount<QueueItem>(consumer);
    ASSERT_EQ(items_in_queue, 5);
    ASSERT_EQ(bad_items, 0);
  }
}
