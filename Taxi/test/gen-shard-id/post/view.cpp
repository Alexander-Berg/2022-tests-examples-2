#include "view.hpp"

#include <userver/formats/bson.hpp>
#include <userver/formats/bson/binary.hpp>
#include <userver/formats/json/inline.hpp>

#include <order-access/order_shards.hpp>

namespace handlers::v1_test_gen_shard_id::post {

Response View::Handle(Request&& request, Dependencies&& deps) {
  const auto body = formats::bson::FromBinaryString(request.body);
  const auto document_opt =
      body["document"].As<std::optional<formats::bson::Document>>();
  formats::bson::Document document;
  if (document_opt) {
    document = *document_opt;
  }

  const auto document_id =
      deps.extra.mongo_wrapper_for_tests->GenerateDocumentId(document);

  const auto response = formats::bson::MakeDoc("_id", document_id);

  return Response200{formats::bson::ToBinaryString(response)};
}

}  // namespace handlers::v1_test_gen_shard_id::post
