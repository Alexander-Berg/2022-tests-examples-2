#include <gtest/gtest.h>

#include <caches/check_in_orders.hpp>

namespace dci = ::models::dispatch::check_in;

namespace handlers {

// Print CheckInOrder if test assertion failed
void PrintTo(const CheckInOrder& order, std::ostream* os) {
  *os << ToString(formats::json::ValueBuilder(order).ExtractValue());
}

}  // namespace handlers

namespace {

auto Time(std::time_t t) { return std::chrono::system_clock::from_time_t(t); };

caches::CheckInOrdersCacheContainer CreateContainer(
    const std::vector<dci::CheckInOrder>& orders) {
  caches::CheckInOrdersCacheContainer container;
  for (const auto& order : orders) {
    container.insert_or_assign(std::string(order.order_id),
                               dci::CheckInOrder(order));
  }

  return container;
}

bool CheckInOrderComparator(const dci::CheckInOrder& lhs,
                            const dci::CheckInOrder& rhs) {
  return lhs.order_id < rhs.order_id;
}

template <typename CheckInOrdersRange>
void Compare(const std::vector<dci::CheckInOrder>& etalon,
             const CheckInOrdersRange& actual) {
  std::vector<dci::CheckInOrder> etalon_sorted(etalon);
  std::sort(etalon_sorted.begin(), etalon_sorted.end(), CheckInOrderComparator);
  std::vector<dci::CheckInOrder> actual_sorted(std::begin(actual),
                                               std::end(actual));
  std::sort(actual_sorted.begin(), actual_sorted.end(), CheckInOrderComparator);
  ASSERT_EQ(etalon_sorted, actual_sorted);
}

}  // namespace

TEST(CheckInOrdersCacheContainer, Empty) {
  caches::CheckInOrdersCacheContainer container;
  for ([[maybe_unused]] const auto& order : container) {
    ASSERT_TRUE(false);
  }
  ASSERT_EQ(container.size(), 0);
}

TEST(CheckInOrdersCacheContainer, Insert) {
  std::vector<dci::CheckInOrder> orders{
      {"order_id1", Time(1), Time(1), std::nullopt, "terminal_id1",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0},
      {"order_id2", Time(3), Time(2), std::nullopt, "terminal_id2",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0},
      {"order_id3", Time(4), Time(3), Time(4), "terminal_id1", "pickup_line1",
       "tariff_zone", "user_id", "phone_id", "device_id", 0},
      {"order_id4", Time(5), Time(3), std::nullopt, "terminal_id3",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0},
  };

  auto container = CreateContainer(orders);
  Compare(orders, container);

  const dci::CheckInOrder replaced_order = {
      "order_id2",
      Time(10),
      Time(2),
      Time(10),
      "terminal_id2",
      "pickup_line1",
      "tariff_zone",
      "user_id",
      "phone_id",
      "device_id",
      0,
  };
  orders[1] = replaced_order;
  container.insert_or_assign("order_id2", dci::CheckInOrder(replaced_order));
  Compare(orders, container);
}

TEST(CheckInOrdersCacheContainer, GetEmpty) {
  caches::CheckInOrdersCacheContainer container;
  ASSERT_EQ(container.Get("order_id0"), nullptr);
}

TEST(CheckInOrdersCacheContainer, Get) {
  const dci::CheckInOrder not_existing_order = {"order_idXXX",
                                                Time(100),
                                                Time(100),
                                                std::nullopt,
                                                "terminal_id1",
                                                std::nullopt,
                                                "tariff_zone",
                                                "user_id",
                                                "phone_id",
                                                "device_id",
                                                0};

  std::vector<dci::CheckInOrder> orders{
      {"order_id1", Time(1), Time(1), std::nullopt, "terminal_id1",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0,
       "econom"},
      {"order_id2", Time(3), Time(2), std::nullopt, "terminal_id2",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0,
       "comfort"},
      {"order_id3", Time(4), Time(3), Time(4), "terminal_id1", "pickup_line1",
       "tariff_zone", "user_id", "phone_id", "device_id", 0, "econom"},
      {"order_id4", Time(5), Time(3), std::nullopt, "terminal_id3",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0,
       "comport"},
  };

  const auto container = CreateContainer(orders);
  for (const auto& order : orders) {
    ASSERT_EQ(*container.Get(order.order_id), order);
  }
  ASSERT_EQ(container.Get(not_existing_order.order_id), nullptr);
}

TEST(CheckInOrdersCacheContainer, GetAllOrdersFromTerminalWithClassEmpty) {
  caches::CheckInOrdersCacheContainer container;
  Compare({}, container.GetAllOrdersFromTerminalWithClass("terminal_id0",
                                                          "econom"));
}

TEST(CheckInOrdersCacheContainer, OrdersCountInTerminal) {
  std::vector<dci::CheckInOrder> orders{
      {"order_id0", Time(1), Time(1), std::nullopt, "terminal_id1",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0,
       "econom"},
      {"order_id1", Time(3), Time(2), std::nullopt, "terminal_id2",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0,
       "comfort"},
      {"order_id2", Time(3), Time(2), std::nullopt, "terminal_id2",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0,
       "econom"},
      {"order_id3", Time(4), Time(3), Time(4), "terminal_id1", "pickup_line1",
       "tariff_zone", "user_id", "phone_id", "device_id", 0, "econom"},
      {"order_id4", Time(4), Time(3), Time(4), "terminal_id1", "pickup_line2",
       "tariff_zone", "user_id", "phone_id", "device_id", 0, "comfort"},
      {"order_id5", Time(1), Time(1), std::nullopt, "terminal_id3",
       std::nullopt, "tariff_zone", "user_id", "phone_id", "device_id", 0,
       "comfortplus"},
  };

  const auto container = CreateContainer(orders);
  Compare({orders[0], orders[3]}, container.GetAllOrdersFromTerminalWithClass(
                                      "terminal_id1", "econom"));
  Compare({orders[4]}, container.GetAllOrdersFromTerminalWithClass(
                           "terminal_id1", "comfort"));
  Compare({orders[1]}, container.GetAllOrdersFromTerminalWithClass(
                           "terminal_id2", "comfort"));
  Compare({orders[2]}, container.GetAllOrdersFromTerminalWithClass(
                           "terminal_id2", "econom"));
  Compare({}, container.GetAllOrdersFromTerminalWithClass("terminal_id1",
                                                          "comfortplus"));
  Compare({}, container.GetAllOrdersFromTerminalWithClass("terminal_id1",
                                                          "unknown_class"));
  Compare({}, container.GetAllOrdersFromTerminalWithClass("terminal_idXXX",
                                                          "econom"));
}
