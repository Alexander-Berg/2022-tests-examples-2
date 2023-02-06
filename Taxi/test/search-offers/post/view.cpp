#include "view.hpp"

#include <userver/formats/bson.hpp>
#include <userver/formats/bson/binary.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/tracing/span.hpp>

namespace handlers::v1_test_search_offers::post {

Response View::Handle(Request&& request, Dependencies&& deps) {
  const auto body = formats::bson::FromBinaryString(request.body);
  const auto request_query = body["query"];
  const auto request_fields = body["fields"];
  const auto request_sort = body["sort"];

  if (request_query.IsMissing() || !request_query.IsDocument()) {
    throw Response400{{"invalid_query", "query must be a non-empty obj"}};
  }
  if (!request_fields.IsMissing() && !request_fields.IsArray()) {
    throw Response400{{"invalid_fields", "fields must be an array"}};
  }
  if (!request_sort.IsMissing() && !request_sort.IsArray()) {
    throw Response400{{"invalid_sort", "sort must be an array"}};
  }

  const auto projection_fields =
      request_fields.As<std::optional<std::vector<std::string>>>();
  std::optional<sharded_mongo_wrapper::SortSettings> sort_settings;

  const auto request_sort_array =
      request_sort.As<std::optional<std::vector<formats::bson::Document>>>();
  if (request_sort_array) {
    using Dir = storages::mongo::options::Sort::Direction;
    sort_settings = sharded_mongo_wrapper::SortSettings{};
    for (const auto& sort_doc : *request_sort_array) {
      const auto sort_field = sort_doc["field"].As<std::string>();
      const auto sort_dir = sort_doc["dir"].As<int>(1);

      Dir dir;
      if (sort_dir == 1)
        dir = Dir::kAscending;
      else if (sort_dir == -1)
        dir = Dir::kDescending;
      else
        throw std::runtime_error("Unexpected sort direction");

      sort_settings->settings_.push_back({sort_field, dir});
    }
  }

  storages::mongo::options::Projection projection;
  if (projection_fields) {
    for (const auto& field : *projection_fields) {
      projection.Include(field);
    }
  }

  const auto read_preference = storages::mongo::options::ReadPreference{
      storages::mongo::options::ReadPreference::Mode::kPrimary};

  auto cursor = deps.extra.mongo_wrapper_for_tests->SearchDocuments(
      request_query, sort_settings, read_preference, projection,
      storages::mongo::options::Limit{0});

  formats::bson::ValueBuilder offers;
  offers["documents"] =
      formats::bson::ValueBuilder(formats::common::Type::kArray);
  for (auto&& doc : cursor) {
    offers["documents"].PushBack(std::move(doc));
  }

  return Response200{formats::bson::ToBinaryString(offers.ExtractValue())};
}

}  // namespace handlers::v1_test_search_offers::post
