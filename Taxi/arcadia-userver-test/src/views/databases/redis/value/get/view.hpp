#pragma once

#include <handlers/databases/redis/value/get/request.hpp>
#include <handlers/databases/redis/value/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::databases_redis_value::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::databases_redis_value::get
