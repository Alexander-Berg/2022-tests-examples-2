#include "view.hpp"
#include <userver/formats/bson.hpp>

namespace handlers::databases_mongo_value::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  auto doc = dependencies.mongo_collections->dump_sample.FindOne(
      formats::bson::MakeDoc("_id", request.key),
      storages::mongo::options::ReadPreference::kSecondaryPreferred);

  response.value = doc.value()["value"].As<std::string>();

  return response;
}

}  // namespace handlers::databases_mongo_value::get
