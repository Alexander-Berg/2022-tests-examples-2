#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/testonly/callsyncprocedure/post/request.hpp>
#include <handlers/testonly/callsyncprocedure/post/response.hpp>

namespace handlers::testonly_callsyncprocedure::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::testonly_callsyncprocedure::post
