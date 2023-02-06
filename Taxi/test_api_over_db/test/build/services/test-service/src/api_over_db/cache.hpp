#pragma once

/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

#include <functional>
#include <string>

#include <optional>

#include <api_base/bucket_locked_cache.hpp>
#include <api_base/bucket_locked_model.hpp>
#include <api_base/bucket_locked_mongo_cache_impl.hpp>
#include <api_base/cache.hpp>
#include <api_base/model.hpp>
#include <storages/mongo_collections/collections.hpp>
#include <storages/mongo_collections/component.hpp>

#include <api_over_db/api_over_db_model.hpp>
#include <api_over_db/custom_key_fetchers.hpp>
#include <api_over_db/dump_context.hpp>
#include <api_over_db/key_fetchers.hpp>

namespace api_over_db::components {
namespace replica1 {

using ItemType = api_over_db::models::replica1::Replica1;

enum class CacheIndexId { kCount };

struct CacheModelTraits {
  static constexpr const char* kLogPrefix = "some1-cache-component : ";
  using ItemType = ItemType;
  using IndicesEnum = CacheIndexId;
  using Timestamp = formats::bson::Timestamp;
  static const std::vector<
      std::function<std::set<std::optional<std::string>>(const ItemType& item)>>
      kKeysByIndex;
  static constexpr bool kEraseDeleted = false;
};

using CacheModel = api_over_db::CacheModel<CacheModelTraits>;

struct CacheTraits {
  static constexpr const char* kName = "some1-cache-component";
  static constexpr const char* kLogPrefix = CacheModelTraits::kLogPrefix;
  using ItemType = ItemType;
  using Model = CacheModel;
  using MongoCollectionsComponent = ::components::MongoCollections;
  static constexpr auto kMongoCollectionsField =
      &storages::mongo::Collections::some1_mongo_collection_name;
  static constexpr const char* kMongoUpdateFieldName = "mongo-some1-updated";
  static constexpr const auto kMongoNewItemsProjection = {
      "mongo-some1-field1",
      "mongo-some1-updated",
  };
  static constexpr const auto& kDumpContext =
      api_over_db::replica1::kDumpContext;
  static constexpr const bool kDoUpdateDeletions = false;
};

using Cache = api_over_db::components::Cache<CacheTraits>;
}
namespace replica2 {

using ItemType = api_over_db::models::replica2::Replica2;

enum class CacheIndexId { kCount };

struct CacheModelTraits {
  static constexpr const char* kLogPrefix = "some2-cache-component : ";
  using ItemType = ItemType;
  using IndicesEnum = CacheIndexId;
  using Timestamp = formats::bson::Timestamp;
  static const std::vector<
      std::function<std::set<std::optional<std::string>>(const ItemType& item)>>
      kKeysByIndex;
  static constexpr bool kEraseDeleted = false;
};

using CacheModel = api_over_db::CacheModel<CacheModelTraits>;

struct CacheTraits {
  static constexpr const char* kName = "some2-cache-component";
  static constexpr const char* kLogPrefix = CacheModelTraits::kLogPrefix;
  using ItemType = ItemType;
  using Model = CacheModel;
  using MongoCollectionsComponent = ::components::MongoCollections;
  static constexpr auto kMongoCollectionsField =
      &storages::mongo::Collections::some2_mongo_collection_name;
  static constexpr const char* kMongoUpdateFieldName = "mongo-some2-updated";
  static constexpr const auto kMongoNewItemsProjection = {
      "mongo-some2-updated",
  };
  static constexpr const auto& kDumpContext =
      api_over_db::replica2::kDumpContext;
  static constexpr const bool kDoUpdateDeletions = false;
};

using Cache = api_over_db::components::Cache<CacheTraits>;
}
namespace replica3 {

using ItemType = api_over_db::models::replica3::Replica3;

enum class CacheIndexId { kCount };

struct CacheModelTraits {
  static constexpr const char* kLogPrefix = "some3-cache-component : ";
  using ItemType = ItemType;
  using IndicesEnum = CacheIndexId;
  using Timestamp = formats::bson::Timestamp;
  static const std::vector<
      std::function<std::set<std::optional<std::string>>(const ItemType& item)>>
      kKeysByIndex;
  static constexpr bool kEraseDeleted = false;
};

using CacheModel = api_over_db::CacheModel<CacheModelTraits>;

struct CacheTraits {
  static constexpr const char* kName = "some3-cache-component";
  static constexpr const char* kLogPrefix = CacheModelTraits::kLogPrefix;
  using ItemType = ItemType;
  using Model = CacheModel;
  using MongoCollectionsComponent = ::components::MongoCollections;
  static constexpr auto kMongoCollectionsField =
      &storages::mongo::Collections::some3_mongo_collection_name;
  static constexpr const char* kMongoUpdateFieldName = "mongo-some3-updated";
  static constexpr const auto kMongoNewItemsProjection = {
      "mongo-some3-field1",
      "mongo-some3-updated",
  };
  static constexpr const auto& kDumpContext =
      api_over_db::replica3::kDumpContext;
  static constexpr const bool kDoUpdateDeletions = false;
};

using Cache = api_over_db::components::Cache<CacheTraits>;
}
}