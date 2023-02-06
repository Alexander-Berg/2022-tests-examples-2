#include "view.hpp"

#include <userver/formats/json/inline.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/assert.hpp>

namespace handlers::v1_client_cache_test::get {

namespace {
formats::json::ValueBuilder ToJson(
    const api_over_db::models::example_pg_with_deletions_client::
        ExamplePgWithDeletionsClient& doc) {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);

  builder["example_id"] = doc.example_id;
  if (doc.some_field.has_value())
    builder["some_field"] = doc.some_field.value();
  builder["updated_ts"] = ::utils::datetime::Timestring(
      doc.updated_ts, "UTC", "%Y-%m-%dT%H:%M:%E*S%z");
  builder["revision"] = doc.revision;
  builder["is_deleted"] = doc.is_deleted;

  return builder;
}
}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  auto cache_name = request.cache_name;
  if (cache_name != "example-pg-with-deletions-client-cache") {
    LOG_WARNING() << "invalid cache name: " << cache_name;
    return Response404{};
  }

  const auto& cache = dependencies.pg_with_deletions_cache;
  if (!cache) {
    LOG_WARNING() << "cache is null";
    return Response404{};
  }

  auto items = cache->BuildItemsMapByTimestamp({}, 1000, false);

  formats::json::ValueBuilder item_array(formats::json::Type::kArray);

  for (const auto& [ts, item] : items) {
    UASSERT_MSG(bool(item.first), "null item in cache");
    if (item.first) {
      auto item_json = ToJson(*item.first);
      item_array.PushBack(std::move(item_json));
    }
  }

  return Response200{{{item_array.ExtractValue()}}};
}

}  // namespace handlers::v1_client_cache_test::get
