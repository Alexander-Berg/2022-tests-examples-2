#pragma once

#include <memory>

#include <userver/storages/mongo/collection.hpp>
#include <userver/storages/mongo/pool.hpp>

namespace storages::mongo {

struct Collections {
  explicit Collections(
      ::storages::mongo::PoolPtr taxi_pool,
      ::storages::mongo::PoolPtr users_pool
  ) :
      cars(taxi_pool->GetCollection("cars")),
      drivers(taxi_pool->GetCollection("drivers")),
      parks(taxi_pool->GetCollection("parks")),
      user_phones(users_pool->GetCollection("user_phones"))
  {}

  ::storages::mongo::Collection cars;
  ::storages::mongo::Collection drivers;
  ::storages::mongo::Collection parks;
  ::storages::mongo::Collection user_phones;
};
using CollectionsPtr = std::shared_ptr<Collections>;

}  // namespace storages::mongo
