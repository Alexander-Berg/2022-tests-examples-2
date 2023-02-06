#include "driver-status/orders_v2.fbs.h"
#include "driver_orders.hpp"
#include "orders_test_helpers.hpp"

#include <algorithm>
#include <cstdlib>
#include <iterator>
#include <memory>
#include <optional>

#include <gzip/gzip.hpp>
#include <userver/utest/utest.hpp>

#include <models/driverid.hpp>

namespace helpers = orders_test_helpers;
using caches::driver_status::CompressionType;
using models::providers::ProviderMapper;

UTEST(OrdersCache, UnpackEmptyString) {
  auto data = helpers::CreateOrdersStorage();
  EXPECT_ANY_THROW(
      models::driver_orders::UnpackInto(*data, "", CompressionType::kGzip));
}

UTEST(OrdersCache, UnpackWithoutItems) {
  auto data = helpers::CreateOrdersStorage();

  namespace fbs = ::driver_status::fbs::v2::orders;
  fbs::ListT list;
  list.revision = 0;
  flatbuffers::FlatBufferBuilder fbb;
  auto packed_list = fbs::List::Pack(fbb, &list);
  fbb.Finish(packed_list);
  std::string buf(gzip::Compress(
      reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
  EXPECT_THROW(
      models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip),
      std::runtime_error);
}

UTEST(OrdersCache, UnpackWithEmptyOrders) {
  auto data = helpers::CreateOrdersStorage();

  namespace fbs = ::driver_status::fbs::v2::orders;
  flatbuffers::FlatBufferBuilder fbb;
  std::vector<::flatbuffers::Offset<fbs::Item>> items_offset;
  flatbuffers::Offset<fbs::List> list_offset =
      helpers::fbs::CreateListDirect(fbb, 0, &items_offset);
  fbb.Finish(list_offset);
  std::string buf(gzip::Compress(
      reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
  EXPECT_NO_THROW(
      models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip));
}

UTEST(OrdersCache, UnpackWrongItems) {
  auto data = helpers::CreateOrdersStorage();

  namespace fbs = ::driver_status::fbs::v2::orders;
  {
    fbs::ListT list;
    fbs::ItemT item;
    item.order_id = "order01";
    item.driver_id = "driver01";
    item.provider = "yandex";
    item.status = fbs::Status_None;
    list.revision = 0;
    list.items.push_back(std::make_unique<fbs::ItemT>(item));

    flatbuffers::FlatBufferBuilder fbb;
    auto packed_list = fbs::List::Pack(fbb, &list);
    fbb.Finish(packed_list);
    std::string buf(gzip::Compress(
        reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
    EXPECT_THROW(
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip),
        std::runtime_error);
  }  // namespace fbs=::driver_status::fbs::v2::orders;
  {
    fbs::ListT list;
    fbs::ItemT item;
    item.park_id = "park01";
    item.driver_id = "driver01";
    item.provider = "yandex";
    item.status = fbs::Status_None;
    list.revision = 0;
    list.items.push_back(std::make_unique<fbs::ItemT>(item));

    flatbuffers::FlatBufferBuilder fbb;
    auto packed_list = fbs::List::Pack(fbb, &list);
    fbb.Finish(packed_list);
    std::string buf(gzip::Compress(
        reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
    EXPECT_THROW(
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip),
        std::runtime_error);
  }  // namespace fbs=::driver_status::fbs::v2::statuses;
  {
    fbs::ListT list;
    fbs::ItemT item;
    item.park_id = "park01";
    item.order_id = "order01";
    item.driver_id = "driver01";
    item.status = fbs::Status_None;
    list.revision = 0;
    list.items.push_back(std::make_unique<fbs::ItemT>(item));

    flatbuffers::FlatBufferBuilder fbb;
    auto packed_list = fbs::List::Pack(fbb, &list);
    fbb.Finish(packed_list);
    std::string buf(gzip::Compress(
        reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
    EXPECT_THROW(
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip),
        std::runtime_error);
  }  // namespace fbs=::driver_status::fbs::v2::statuses;
  {
    fbs::ListT list;
    fbs::ItemT item;
    item.park_id = "park01";
    item.order_id = "order01";
    item.driver_id = "driver01";
    item.provider = "yandex";
    item.status = fbs::Status_None;
    list.revision = 0;
    list.items.push_back(std::make_unique<fbs::ItemT>(item));

    flatbuffers::FlatBufferBuilder fbb;
    auto packed_list = fbs::List::Pack(fbb, &list);
    fbb.Finish(packed_list);
    std::string buf(gzip::Compress(
        reinterpret_cast<const char*>(fbb.GetBufferPointer()), fbb.GetSize()));
    EXPECT_NO_THROW(
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip));
  }
}

TEST(OrdersCache, UnpackDrivers) {
  auto data = helpers::CreateOrdersStorage();

  namespace fbs = ::driver_status::fbs::v2::orders;
  const std::size_t kOrdersCount = 10;
  const std::chrono::microseconds kRevisionExpected(15);

  {
    std::vector<helpers::Order> orders;
    auto statistics =
        GenerateDriverOrders(std::back_inserter(orders), 0, kOrdersCount);

    std::string buf(
        PackOrders(orders.begin(), orders.end(), kRevisionExpected));
    auto result =
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip);

    EXPECT_EQ(result.reads_count, kOrdersCount);
    EXPECT_EQ(result.erases_count, 0);
    EXPECT_EQ(result.errors_count, 0);
    EXPECT_EQ(result.revision,
              std::chrono::system_clock::time_point(kRevisionExpected));
    EXPECT_EQ(helpers::CountOrders(*data),
              statistics.active_orders - statistics.finished_orders);

    for (const auto& item : orders) {
      const auto dbid_uuid =
          models::DriverId::MakeDbidUuid(item.park_id, item.driver_id);
      const auto data_iter = data->find(dbid_uuid);
      EXPECT_NE(data_iter, data->end());
      const auto order_iter =
          std::find_if(data_iter->second->begin(), data_iter->second->end(),
                       [&item](const auto& order) {
                         return order.order_id == item.order_id;
                       });
      EXPECT_NE(order_iter, data_iter->second->end());
      EXPECT_EQ(ProviderMapper::GetName(order_iter->provider), item.provider);
    }
  }
  // adding new orders
  {
    std::vector<helpers::Order> orders;
    auto statistics = GenerateDriverOrders(std::back_inserter(orders),
                                           kOrdersCount, 2 * kOrdersCount);
    const auto prev_size = helpers::CountOrders(*data);

    std::string buf(
        PackOrders(orders.begin(), orders.end(), kRevisionExpected));
    auto result =
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip);

    EXPECT_EQ(result.reads_count, kOrdersCount);
    EXPECT_EQ(result.erases_count, 0);
    EXPECT_EQ(result.errors_count, 0);
    EXPECT_EQ(result.revision,
              std::chrono::system_clock::time_point(kRevisionExpected));
    EXPECT_EQ(
        helpers::CountOrders(*data),
        prev_size + statistics.active_orders - statistics.finished_orders);

    for (const auto& item : orders) {
      const auto dbid_uuid =
          models::DriverId::MakeDbidUuid(item.park_id, item.driver_id);
      const auto data_iter = data->find(dbid_uuid);
      EXPECT_NE(data_iter, data->end());
      const auto order_iter =
          std::find_if(data_iter->second->begin(), data_iter->second->end(),
                       [&item](const auto& order) {
                         return order.order_id == item.order_id;
                       });
      EXPECT_NE(order_iter, data_iter->second->end());
      EXPECT_EQ(ProviderMapper::GetName(order_iter->provider), item.provider);
    }
  }
  // adding extra orders for each driver
  {
    std::vector<helpers::Order> orders;
    auto statistics =
        GenerateDriverOrders(std::back_inserter(orders), 0, 2 * kOrdersCount,
                             "driver", "park", "second_order");
    const auto prev_size = helpers::CountOrders(*data);

    std::string buf(
        PackOrders(orders.begin(), orders.end(), kRevisionExpected));
    auto result =
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip);

    EXPECT_EQ(result.reads_count, 2 * kOrdersCount);
    EXPECT_EQ(result.erases_count, 0);
    EXPECT_EQ(result.errors_count, 0);
    EXPECT_EQ(result.revision,
              std::chrono::system_clock::time_point(kRevisionExpected));
    EXPECT_EQ(
        helpers::CountOrders(*data),
        prev_size + statistics.active_orders - statistics.finished_orders);

    for (const auto& item : orders) {
      const auto dbid_uuid =
          models::DriverId::MakeDbidUuid(item.park_id, item.driver_id);
      const auto data_iter = data->find(dbid_uuid);
      EXPECT_NE(data_iter, data->end());
      const auto order_iter =
          std::find_if(data_iter->second->begin(), data_iter->second->end(),
                       [&item](const auto& order) {
                         return order.order_id == item.order_id;
                       });
      EXPECT_NE(order_iter, data_iter->second->end());
      EXPECT_EQ(ProviderMapper::GetName(order_iter->provider), item.provider);
    }
  }
  // removing half of orders
  {
    std::vector<helpers::Order> orders;
    auto statistics =
        GenerateDriverOrders(std::back_inserter(orders), 0, 2 * kOrdersCount,
                             "driver", "park", "order", fbs::Status_Complete);
    const auto prev_size = helpers::CountOrders(*data);

    std::string buf(
        PackOrders(orders.begin(), orders.end(), kRevisionExpected));
    auto result =
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip);

    EXPECT_EQ(result.reads_count, 2 * kOrdersCount);
    EXPECT_EQ(result.erases_count, 2 * kOrdersCount);
    EXPECT_EQ(result.errors_count, 0);
    EXPECT_EQ(result.revision,
              std::chrono::system_clock::time_point(kRevisionExpected));
    EXPECT_EQ(
        helpers::CountOrders(*data),
        prev_size - statistics.finished_orders + statistics.active_orders);

    for (const auto& item : orders) {
      const auto dbid_uuid =
          models::DriverId::MakeDbidUuid(item.park_id, item.driver_id);
      const auto data_iter = data->find(dbid_uuid);
      if (item.status != fbs::Status_Complete) {
        EXPECT_NE(data_iter, data->end());
        const auto order_iter =
            std::find_if(data_iter->second->begin(), data_iter->second->end(),
                         [&item](const auto& order) {
                           return order.order_id == item.order_id;
                         });
        EXPECT_NE(order_iter, data_iter->second->end());
        EXPECT_EQ(ProviderMapper::GetName(order_iter->provider), item.provider);
      } else {
        if (data_iter != data->end()) {
          const auto order_iter =
              std::find_if(data_iter->second->begin(), data_iter->second->end(),
                           [&item](const auto& order) {
                             return order.order_id == item.order_id;
                           });
          EXPECT_EQ(order_iter, data_iter->second->end());
        }
      }
    }
  }
  // removing the rest orders
  {
    std::vector<helpers::Order> orders;
    GenerateDriverOrders(std::back_inserter(orders), 0, 2 * kOrdersCount,
                         "driver", "park", "second_order",
                         fbs::Status_Complete);

    std::string buf(
        PackOrders(orders.begin(), orders.end(), kRevisionExpected));
    auto result =
        models::driver_orders::UnpackInto(*data, buf, CompressionType::kGzip);

    EXPECT_EQ(result.reads_count, 2 * kOrdersCount);
    EXPECT_EQ(result.erases_count, 2 * kOrdersCount);
    EXPECT_EQ(result.errors_count, 0);
    EXPECT_EQ(result.revision,
              std::chrono::system_clock::time_point(kRevisionExpected));
    EXPECT_TRUE(data->empty());
  }
}
