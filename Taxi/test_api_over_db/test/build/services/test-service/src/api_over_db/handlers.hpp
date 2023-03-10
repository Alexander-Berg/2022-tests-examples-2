#pragma once

/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

#include <userver/formats/bson/value_builder.hpp>

#include <api_base/handlers/bucket_locked_updates.hpp>
#include <api_base/handlers/proxy_retrieve.hpp>
#include <api_base/handlers/retrieve.hpp>
#include <api_base/handlers/retrieve_by_index.hpp>
#include <api_base/handlers/updates.hpp>
#include <storages/mongo_collections/collections.hpp>
#include <storages/mongo_collections/component.hpp>

#include <api_over_db/cache.hpp>

namespace api_over_db::handlers {
namespace proxy1 {

// implement this function by hand
// throw server::handlers::RequestParseError on incorrect id format
// other exceptions will result in 500
formats::bson::ValueBuilder GetMongoFilterForId(const std::string& id);

struct ProxyRetrieveTraits {
  static constexpr const char* kName = "some2-proxy-retrieve-component";
  static constexpr const char* kHandlerName = "v2/proxy_retrieve";
  static constexpr const char* kArrayName = "some2-retrieve-data";
  static constexpr const char* kJsonIdFieldName = "json-some2-id";

  static constexpr const auto& kGetMongoFilterForId = &GetMongoFilterForId;

  using ModelItemType = api_over_db::models::proxy1::Proxy1;
  using MongoCollectionsComponent = ::components::MongoCollections;
  static constexpr auto kMongoCollectionsField =
      &storages::mongo::Collections::some2_mongo_collection_name;
  static constexpr const auto kMongoProjection = {};
  static constexpr const auto& kAllJsonFields =
      api_over_db::models::proxy1::GetAllJsonFields;
};

using ProxyRetrieve = api_over_db::handlers::ProxyRetrieve<ProxyRetrieveTraits>;

}
namespace replica1 {

struct UpdatesTraits {
  static constexpr const char* kName = "some1-updates-component";
  static constexpr const char* kHandlerName = "v1/updates";
  static constexpr const char* kArrayName = "some1-updates-data";
  using CacheType = api_over_db::components::replica1::Cache;
  using Timestamp = CacheType::Timestamp;
  static constexpr const auto& kAllJsonFields =
      api_over_db::models::replica1::GetAllJsonFields;
};

using Updates = api_over_db::handlers::Updates<UpdatesTraits>;

struct RetrieveTraits {
  static constexpr const char* kName = "some1-retrieve-component";
  static constexpr const char* kHandlerName = "v1/retrieve";
  static constexpr const char* kArrayName = "some1-retrieve-data";
  static constexpr const char* kIdField = "json-some1-id";
  using ModelItemType = api_over_db::models::replica1::Replica1;
  using CacheType = api_over_db::components::replica1::Cache;
  static constexpr const auto& kAllJsonFields =
      api_over_db::models::replica1::GetAllJsonFields;
};

using Retrieve = api_over_db::handlers::Retrieve<RetrieveTraits>;

}
namespace replica2 {

struct UpdatesTraits {
  static constexpr const char* kName = "some2-updates-component";
  static constexpr const char* kHandlerName = "v2/updates";
  static constexpr const char* kArrayName = "some2-updates-data";
  using CacheType = api_over_db::components::replica2::Cache;
  using Timestamp = CacheType::Timestamp;
  static constexpr const auto& kAllJsonFields =
      api_over_db::models::replica2::GetAllJsonFields;
};

using Updates = api_over_db::handlers::Updates<UpdatesTraits>;

struct RetrieveTraits {
  static constexpr const char* kName = "some2-retrieve-component";
  static constexpr const char* kHandlerName = "v2/retrieve";
  static constexpr const char* kArrayName = "some2-retrieve-data";
  static constexpr const char* kIdField = "json-some2-id";
  using ModelItemType = api_over_db::models::replica2::Replica2;
  using CacheType = api_over_db::components::replica2::Cache;
  static constexpr const auto& kAllJsonFields =
      api_over_db::models::replica2::GetAllJsonFields;
};

using Retrieve = api_over_db::handlers::Retrieve<RetrieveTraits>;

}
namespace replica3 {

struct UpdatesTraits {
  static constexpr const char* kName = "some3-updates-component";
  static constexpr const char* kHandlerName = "v3/updates";
  static constexpr const char* kArrayName = "some3-updates-data";
  using CacheType = api_over_db::components::replica3::Cache;
  using Timestamp = CacheType::Timestamp;
  static constexpr const auto& kAllJsonFields =
      api_over_db::models::replica3::GetAllJsonFields;
};

using Updates = api_over_db::handlers::Updates<UpdatesTraits>;

struct RetrieveTraits {
  static constexpr const char* kName = "some3-retrieve-component";
  static constexpr const char* kHandlerName = "v3/retrieve";
  static constexpr const char* kArrayName = "some3-retrieve-data";
  static constexpr const char* kIdField = "json-some3-id";
  using ModelItemType = api_over_db::models::replica3::Replica3;
  using CacheType = api_over_db::components::replica3::Cache;
  static constexpr const auto& kAllJsonFields =
      api_over_db::models::replica3::GetAllJsonFields;
};

using Retrieve = api_over_db::handlers::Retrieve<RetrieveTraits>;

}
}
