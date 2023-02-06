#include "view.hpp"

#include <handlers/dependencies.hpp>

namespace handlers::tests_v1_cleanup_scope_queue::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  if (!dependencies.extra.processing_ng.CheckAllowedAndCleanupProcessingState(
          request.scope, request.queue)) {
    return Response404();
  }
  return Response200();
}

}  // namespace handlers::tests_v1_cleanup_scope_queue::post
