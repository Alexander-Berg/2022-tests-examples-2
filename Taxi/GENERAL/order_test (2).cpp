#include "order.hpp"

#include <userver/dump/test_helpers.hpp>

#include <gtest/gtest.h>

namespace eats_restapp_marketing::models {

TEST(OrderStatsContainerDump, TestReadWriteSimple) {
  std::unordered_map<PlaceId, std::vector<OrderStats>> source;
  source[PlaceId(1)] = {};
  source[PlaceId(2)] = {};
  source[PlaceId(3)] = {};

  const auto container = OrderStatsContainer(std::move(source));
  dump::TestWriteReadCycle(container);
}

}  // namespace eats_restapp_marketing::models
