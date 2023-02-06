#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test/gen-shard-id/post/request.hpp>
#include <handlers/v1/test/gen-shard-id/post/response.hpp>

namespace handlers::v1_test_gen_shard_id::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_gen_shard_id::post
