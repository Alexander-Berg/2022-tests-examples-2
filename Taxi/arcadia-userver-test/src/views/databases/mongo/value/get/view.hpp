#pragma once

#include <handlers/databases/mongo/value/get/request.hpp>
#include <handlers/databases/mongo/value/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::databases_mongo_value::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::databases_mongo_value::get
