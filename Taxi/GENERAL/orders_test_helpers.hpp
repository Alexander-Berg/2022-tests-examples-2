#pragma once

#include "driver_orders.hpp"

#include <algorithm>
#include <cstdlib>
#include <iterator>
#include <memory>
#include <numeric>
#include <optional>

#include <gzip/gzip.hpp>

#include <driver-status/orders_v2.fbs.h>

namespace orders_test_helpers {
namespace fbs = ::driver_status::fbs::v2::orders;

struct Order {
  std::string driver_id;
  std::string park_id;
  std::string order_id;
  std::string provider;
  fbs::Status status;
};

struct Statistics {
  std::size_t finished_orders{};
  std::size_t active_orders{};
};

template <class Inserter>
Statistics GenerateDriverOrders(Inserter inserter, std::size_t first_idx,
                                std::size_t last_idx,
                                const std::string& driver_id_prefix = "driver",
                                const std::string& park_id_prefix = "park",
                                const std::string& order_id_prefix = "order",
                                fbs::Status status = fbs::Status_Transporting) {
  Statistics result;
  for (auto i = first_idx; i < last_idx; ++i) {
    const auto idx_str = std::to_string(i);
    auto order_id = order_id_prefix + idx_str;

    *inserter = Order{driver_id_prefix + idx_str, park_id_prefix + idx_str,
                      std::move(order_id), "yandex", status};
    if (status == fbs::Status_Complete)
      ++result.finished_orders;
    else
      ++result.active_orders;
  }
  return result;
}

template <class InputIterator>
std::string PackOrders(InputIterator begin, InputIterator end,
                       std::chrono::microseconds revision) {
  flatbuffers::FlatBufferBuilder fbb;
  std::vector<::flatbuffers::Offset<fbs::Item>> items_offset;
  for (auto i = begin; i < end; ++i) {
    const auto driver_id_off = fbb.CreateString(i->driver_id);
    const auto park_id_off = fbb.CreateString(i->park_id);
    const auto order_id_off = fbb.CreateString(i->order_id);
    const auto provider_off = fbb.CreateString(i->provider);
    items_offset.push_back(::driver_status::fbs::v2::orders::CreateItem(
        fbb, driver_id_off, park_id_off, order_id_off, i->status, provider_off,
        revision.count()));
  }
  flatbuffers::Offset<fbs::List> list_offset =
      fbs::CreateListDirect(fbb, revision.count(), &items_offset);
  fbb.Finish(list_offset);
  return gzip::Compress(reinterpret_cast<const char*>(fbb.GetBufferPointer()),
                        fbb.GetSize());
}

inline std::shared_ptr<models::driver_orders::Storage> CreateOrdersStorage() {
  return std::make_unique<models::driver_orders::Storage>();
}

inline std::size_t CountOrders(const models::driver_orders::Storage& storage) {
  std::size_t result = 0;
  for (const auto& drv : storage) result += drv.second->size();
  return result;
}
}  // namespace orders_test_helpers
