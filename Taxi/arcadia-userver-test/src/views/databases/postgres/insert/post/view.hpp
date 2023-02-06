#pragma once

#include <handlers/databases/postgres/insert/post/request.hpp>
#include <handlers/databases/postgres/insert/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::databases_postgres_insert::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::databases_postgres_insert::post
