#include "view.hpp"

#include <userver/storages/redis/client.hpp>

namespace handlers::databases_redis_value::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  auto client = dependencies.redis_arcadia_test.get();

  auto value = client->Get(request.key, {});

  response.value = value.Get().value();

  return response;
}

}  // namespace handlers::databases_redis_value::get
