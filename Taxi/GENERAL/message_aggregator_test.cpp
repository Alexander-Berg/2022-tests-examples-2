#include <geobus/utils/message_aggregator.hpp>

#include <gtest/gtest.h>
#include <numeric>
#include <userver/utest/utest.hpp>

namespace geobus::utils {
class MessageAggregatorTester {
 public:
  template <typename T>
  static void Aggregate(MessageAggregator<T>& aggregator) {
    aggregator.Aggregate();
  }
};
}  // namespace geobus::utils

UTEST(message_aggregator, base) {
  using Message = int;
  using Aggregated = std::vector<int>;

  const size_t count = 950;
  const size_t elements_per_message = 100;
  const auto period = std::chrono::milliseconds(100500);

  /// Input data
  std::vector<Message> inputs(count);
  std::iota(inputs.begin(), inputs.end(), 0);

  /// output data
  std::vector<Aggregated> ret;

  auto callback = [&ret](const Aggregated& value) mutable {
    ret.push_back(value);
  };
  geobus::utils::MessageAggregator<Message> aggregator(
      "test", std::move(callback), period, elements_per_message);
  aggregator.EnablePublishing(true);

  for (auto&& i : inputs) {
    aggregator.Publish(std::move(i));
  }
  geobus::utils::MessageAggregatorTester::Aggregate(aggregator);

  ASSERT_EQ(10ul, ret.size());
  for (size_t i = 0; i < 9; ++i) {
    ASSERT_EQ(100ul, ret[i].size());
  }
  ASSERT_EQ(50ul, ret[9].size());
}
