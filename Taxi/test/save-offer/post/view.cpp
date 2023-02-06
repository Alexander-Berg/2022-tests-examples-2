#include "view.hpp"

#include <userver/formats/bson.hpp>
#include <userver/formats/bson/binary.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/tracing/span.hpp>

namespace handlers::v1_test_save_offer::post {

Response View::Handle(Request&& request, Dependencies&& deps) {
  const auto body = formats::bson::FromBinaryString(request.body);
  const auto offer_payload = body["payload"].As<formats::bson::Document>();
  const auto is_mdb_only = body["mdb_only"].As<bool>(false);

  const auto result = [&]() {
    if (is_mdb_only) {
      return deps.extra.mdb_mongo_wrapper.CreateDocument(offer_payload);
    } else {
      return deps.extra.mongo_wrapper_for_tests->CreateDocument(offer_payload);
    }
  }();
  const auto saved_doc = result.FoundDocument();

  if (!saved_doc) {
    throw std::runtime_error("failed to save offer");
  }

  const auto id = (*saved_doc)["_id"].ConvertTo<std::string>();

  const auto response =
      formats::bson::MakeDoc("document", formats::bson::MakeDoc("_id", id));

  return Response200{formats::bson::ToBinaryString(response)};
}

}  // namespace handlers::v1_test_save_offer::post
