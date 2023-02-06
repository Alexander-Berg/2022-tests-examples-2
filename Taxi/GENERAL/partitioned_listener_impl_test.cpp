#include <listeners/partitioned_listener.hpp>

#include <algorithm>
#include <array>
#include <memory>
#include <vector>

#include <userver/utest/utest.hpp>

#include <channels/positions/traits.hpp>

#include <geobus/channels/positions/listener.hpp>
#include <geobus/subscription/subscription_strategy.hpp>
#include <listeners/client_listener_impl.hpp>

namespace {

using SubscriptionStrategy = geobus::subscription::SubscriptionStrategy;
using Partitions = SubscriptionStrategy::PartitionIndexContainer;

class Subscriber {
 public:
  auto Calls() const { return subscribe_count_ + unsubscribe_count_; }
  auto SubscribeCalls() const { return subscribe_count_; }

  void Subscribe() { ++subscribe_count_; }
  void Unsubscribe() { ++unsubscribe_count_; }

 private:
  int subscribe_count_{0};
  int unsubscribe_count_{0};
};

auto MakeSubscribers(size_t size) {
  std::vector<std::unique_ptr<Subscriber>> result(
      geobus::utils::Reserved{size});
  for (size_t i = 0; i < size; ++i) {
    result.emplace_back(std::make_unique<Subscriber>());
  }
  return result;
}

bool IsSorted(const Partitions& partitions) {
  return std::is_sorted(partitions.begin(), partitions.end());
}

struct TestPartitionedListenerImpl
    : public ::testing::TestWithParam<Partitions> {};

auto MakeTestData() {
  return std::array{
      // clang-format off
    Partitions{0u},
    Partitions{1u},
    Partitions{0u, 2u},
    Partitions{1u, 3u},
    Partitions{0u, 2u, 4u},
    Partitions{1u, 3u, 5u},
    Partitions{0u, 3u},
    Partitions{1u, 4u},
    Partitions{2u, 5u},
    Partitions{0u, 10u, 100u}
      // clang-format on
  };
}

TEST_P(TestPartitionedListenerImpl, ExactlyOneSubscribeOnUnsubscribeCall) {
  const auto& partitions = GetParam();
  ASSERT_FALSE(partitions.empty());
  ASSERT_TRUE(IsSorted(partitions));
  auto subscribers = MakeSubscribers(partitions.back() + 1ull);

  geobus::clients::impl::SubscribeTo(subscribers, partitions);

  for (const auto& subscriber : subscribers) {
    ASSERT_EQ(subscriber->Calls(), 1);
  }
  for (const size_t partition : partitions) {
    ASSERT_EQ(subscribers[partition]->SubscribeCalls(), 1);
  }
}

INSTANTIATE_TEST_SUITE_P(TestPartitionedListenerImpl,
                         TestPartitionedListenerImpl,
                         ::testing::ValuesIn(MakeTestData()));

TEST(TestListenerBuilder, NewListenersShareStats) {
  using Listener = geobus::clients::PositionsListener;
  using ListenerBuilder = geobus::clients::impl::ListenerBuilder<Listener>;

  auto callback = [](const std::string&, Listener::Payload&&) {};

  const ListenerBuilder builder{nullptr, "channel-name", callback};

  auto base_channel = builder.MakeBaseChannelListener();
  auto partition_channel = builder.MakeListenerForPartition(666u);

  ASSERT_NE(&base_channel->GetStats(), &partition_channel->GetStats());
}

}  // namespace
