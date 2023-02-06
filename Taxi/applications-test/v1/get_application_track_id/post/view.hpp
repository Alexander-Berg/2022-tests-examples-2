#pragma once

#include <handlers/applications-test/v1/get_application_track_id/post/request.hpp>
#include <handlers/applications-test/v1/get_application_track_id/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::applications_test_v1_get_application_track_id::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::applications_test_v1_get_application_track_id::post
