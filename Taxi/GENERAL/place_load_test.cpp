#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include "place_load.hpp"

namespace {
using namespace clients::eats_picker_supply;

SelectStoreResponseStoresAPickersA BuildPicker(const std::string& picker_id,
                                               const std::string& eats_id,
                                               int64_t place_id) {
  const auto now = ::utils::datetime::Now();
  SelectStoreResponseStoresAPickersA picker;
  picker.picker_id = picker_id;
  picker.order.emplace(SelectStoreResponseStoresAPickersAOrder{
      eats_id, OrderState::kNew, now, std::chrono::seconds(0), place_id});

  return picker;
}
}  // namespace

TEST(ExtractCurrentlyPickingOrders, UseRightPlaceId) {
  using namespace eats_picker_dispatch::utils;
  const int64_t order_place_id = 2;
  const std::string picker_id = "picker_id";
  const std::string eats_id = "eats_id";
  const auto picker = BuildPicker(picker_id, eats_id, order_place_id);
  PlacePickersMap place_pickers;
  place_pickers[1] = {picker};
  place_pickers[order_place_id] = {picker};
  place_pickers[3] = {picker};
  const auto currently_picking_orders =
      ExtractCurrentlyPickingOrders(place_pickers);

  EXPECT_EQ(currently_picking_orders.size(), 1);
  const auto& actual_order = currently_picking_orders[0];
  EXPECT_EQ(actual_order.place_id, order_place_id);
}
