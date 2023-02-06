#include "view.hpp"

#include <userver/formats/bson.hpp>
#include <userver/storages/mongo/options.hpp>

namespace handlers::v1_test_get_fields::post {

Response View::Handle(Request&& request, Dependencies&& deps) {
  using storages::mongo::options::ReadPreference;

  const auto body = formats::bson::FromBinaryString(request.body);
  const auto filter = body["filter"].As<formats::bson::Document>();
  storages::mongo::options::Projection projection{};
  for (const auto& field : body["fields"]) {
    const std::string field_str = field.As<std::string>();
    projection.Include(field_str);
  }

  ReadPreference read_preference(request.require_latest
                                     ? ReadPreference::kPrimary
                                     : ReadPreference::kSecondaryPreferred);

  const auto document = deps.extra.mongo_wrapper_for_tests->FindDocument(
      request.document_id, filter, read_preference, projection);

  if (!document) {
    throw Response404({"no_such_order", "no such order"});
  }

  const auto response = formats::bson::MakeDoc("document", *document);
  return Response200{formats::bson::ToBinaryString(response)};
}

}  // namespace handlers::v1_test_get_fields::post
