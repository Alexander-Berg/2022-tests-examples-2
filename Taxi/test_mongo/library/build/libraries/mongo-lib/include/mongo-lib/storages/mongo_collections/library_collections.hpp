#pragma once

#include <memory>
#include <unordered_map>

#include <userver/storages/mongo/collection.hpp>
#include <userver/storages/mongo/pool.hpp>

namespace mongo_lib::mongo {

struct Collections {
  explicit Collections(
    const std::unordered_map<std::string, storages::mongo::PoolPtr>& mongo_pools
  ) :
      cars(mongo_pools.at("taxi")->GetCollection("cars")),
      drivers(mongo_pools.at("taxi")->GetCollection("drivers")),
      parks(mongo_pools.at("taxi")->GetCollection("parks")),
      user_phones(mongo_pools.at("users")->GetCollection("user_phones"))
  {}

  ::storages::mongo::Collection cars;
  ::storages::mongo::Collection drivers;
  ::storages::mongo::Collection parks;
  ::storages::mongo::Collection user_phones;
};
using CollectionsPtr = std::shared_ptr<Collections>;

}  // namespace mongo_lib::mongo
