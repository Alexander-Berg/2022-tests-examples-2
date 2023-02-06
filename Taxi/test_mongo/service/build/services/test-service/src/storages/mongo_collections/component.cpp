#include <storages/mongo_collections/component.hpp>
#include <storages/mongo_collections/collections.hpp>

#include <userver/storages/mongo/component.hpp>
#include <userver/components/component.hpp>

namespace components {

MongoCollections::MongoCollections(const ComponentConfig& /*config*/,
                                   const ComponentContext& context) {
  mongo_pools_["taxi"] = context.FindComponent<Mongo>("mongo-taxi").GetPool();
  mongo_pools_["users"] = context.FindComponent<Mongo>("mongo-users").GetPool();
  collections_ = std::make_shared<storages::mongo::Collections>(
    mongo_pools_["taxi"],
    mongo_pools_["users"]
  );
}

MongoCollections::~MongoCollections() = default;

}  // namespace components
